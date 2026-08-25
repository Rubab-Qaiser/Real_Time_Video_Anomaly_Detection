"""
dashboard_client.py

Phase 5.4 — Pushes MegaAlertManager incidents to the Sentinel FastAPI
backend. Designed to be wired in as MegaAlertManager(on_alert=...), so it
is called once per new, de-duplicated incident (not once per frame).

Network calls run on a background worker thread via a small queue, so a
slow or unreachable backend can never stall the real-time detection loop.
"""

import os
import queue
import threading
import time

import requests
import csv
from pathlib import Path

def _load_local_env_if_present():
    """Load system/.env without requiring python-dotenv to be installed."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if key and not os.environ.get(key):
            os.environ[key] = value.strip('"').strip("'")


_load_local_env_if_present()


def _env_dashboard_ip() -> str:
    """Dashboard host from environment, defaulting to localhost."""
    return os.environ.get("DASHBOARD_IP", "127.0.0.1")


def _env_dashboard_port() -> int:
    """Dashboard port from environment, defaulting to 5000."""
    return int(os.environ.get("DASHBOARD_PORT", 5000))


def _env_dashboard_email() -> str:
    """
    Dashboard login email from environment.

    No hardcoded default is shipped so credentials are never committed.
    If unset, consumers must supply a value explicitly.
    """
    return os.environ.get("DASHBOARD_EMAIL", "")


def _env_dashboard_password() -> str:
    """
    Dashboard login password from environment.

    No hardcoded default is shipped so credentials are never committed.
    If unset, consumers must supply a value explicitly.
    """
    return os.environ.get("DASHBOARD_PASSWORD", "")

# Sentinel's own alert vocabulary (from MegaAlertManager) -> dashboard
# incident types. Extend this map if you add new alert_types upstream.
TYPE_MAP = {
    "fall": "Fall",
    "fight": "Fight",
    "running": "Running",
    "fire": "Fire",
    "smoke": "Smoke",
    "crowd": "Crowd",
    "object_anomaly": "Unwanted Object",
}


def _normalize_confidence(confidence):
    """Normalize confidence values to the project-wide 0-100 percentage scale."""
    if confidence is None:
        return None
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        return None
    if confidence <= 1.0:
        confidence *= 100.0
    return max(0.0, min(100.0, confidence))


SEVERITY_MAP = {
    "fall": "critical",
    "fight": "critical",
    "fire": "critical",
    "smoke": "high",
    "running": "high",
    "crowd": "medium",
    "object_anomaly": "medium",
}

# Default confidence per alert type, used when the detection pipeline does
# not provide a real confidence value. Without this, every live-detected
# incident would be stored with 0.0 confidence and show "0%" on the
# dashboard. Values mirror the seed data so live and demo incidents look
# consistent.
CONFIDENCE_MAP = {
    "fall": 92.0,
    "fight": 94.0,
    # "fire": 90.0,  <-- removed per request (prefer explicit model confidence)
    "smoke": 87.0,
    "running": 85.0,
    "crowd": 76.0,
    "object_anomaly": 78.0,
}


class DashboardClient:
    """
    Usage:
        client = DashboardClient(dashboard_ip="192.168.1.50")
        alert_manager = MegaAlertManager(..., on_alert=client.send_detection)

    send_detection(alert_type, frame_path, banned_objects_counts) matches
    the on_alert(alert_type, frame_path, banned_objects_counts) signature
MegaAlertManager.maybe_log() calls.
    """

    def __init__(
        self,
        dashboard_ip: str = None,
        dashboard_port: int = None,
        email: str = None,
        password: str = None,
        camera_id: int = 1,
        location: str = "Main Entrance",
        request_timeout: float = 5.0,
        perf_log_path: str = None,
    ):
        # Prefer explicit arguments, falling back to environment variables.
        # Credentials are never hardcoded so nothing sensitive is committed.
        self.dashboard_ip = dashboard_ip or _env_dashboard_ip()
        self.dashboard_port = dashboard_port or _env_dashboard_port()
        self.email = email or _env_dashboard_email()
        self.password = password or _env_dashboard_password()
        if not self.email or not self.password:
            print("[DashboardClient] Missing DASHBOARD_EMAIL / DASHBOARD_PASSWORD in system/.env or environment.")
        self.camera_id = camera_id
        self.location = location
        self.request_timeout = request_timeout
        # Optional performance logging CSV. If provided, write rows for each
        # incident/status POST with timestamps so offline analysis can compute
        # enqueue delays, post durations and request round-trip times.
        self.perf_log_path = Path(perf_log_path) if perf_log_path else None
        if self.perf_log_path:
            try:
                self.perf_log_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        self.base_url = f"http://{self.dashboard_ip}:{self.dashboard_port}/api"

        self.token = None
        self._login()

        # Background worker so requests.post() never blocks the main
        # detection loop, even on a flaky network.
        self._queue: "queue.Queue" = queue.Queue()
        self._stop_flag = threading.Event()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True, name="DashboardClientWorker")
        self._worker.start()

    # --- auth ---------------------------------------------------------

    def _login(self) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=self.request_timeout,
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                print("[DashboardClient] Connected to Sentinel dashboard")
                return True
            print(f"[DashboardClient] Login failed: HTTP {response.status_code}")
            return False
        except Exception as e:
            print(f"[DashboardClient] Login error: {e}")
            return False

    # --- public API (called from MegaAlertManager.maybe_log) ----------

    def send_detection(self, alert_type: str, frame_path: str, banned_objects_counts: dict = None, confidence: float = None):
        """Non-blocking: enqueues the incident and returns immediately.

        The enqueued tuple includes an `enqueue_ts` so the worker can log
        queue delay vs post time when `perf_log_path` is set.
        """
        # callers may send 0-1 floats or 0-100 percentages; normalize to the system standard.
        normalized_confidence = _normalize_confidence(confidence)
        self._queue.put(("incident", alert_type, frame_path, banned_objects_counts, normalized_confidence, time.time()))

    def send_detection_status(self, fire: bool = False, smoke: bool = False,
                              crowd: bool = False, detections: list = None,
                              camera_id: int = None,
                              area_m2: float = None,
                              density_people_per_m2: float = None,
                              zone_densities: list = None,
                              head_positions_world: list = None,
                              events: list = None):
        """
        Push live detection status snapshot to the Flask backend's
        POST /api/detections/status endpoint.  Non-blocking.

        Called periodically from the detection pipeline to ensure the
        front-end /detections/latest returns real-time YOLO results
        instead of trying to open its own camera (which would 503 when
        the webcam is already held by this process).

        New optional fields (Phase 5.5) forwarded to the dashboard:
          - area_m2, density_people_per_m2, zone_densities, head_positions_world:
            CrowdStatus area/density metrics.
          - events: list of standardized event dicts (fall/running/fight).
        """
        if detections is None:
            detections = []
        cam_id = camera_id if camera_id is not None else self.camera_id
        # include enqueue timestamp for perf logging
        status_payload = ({
            "fire": fire,
            "smoke": smoke,
            "crowd": crowd,
            "detections": detections,
            "camera_id": cam_id,
            "area_m2": area_m2,
            "density_people_per_m2": density_people_per_m2,
            "zone_densities": zone_densities or [],
            "head_positions_world": head_positions_world or [],
            "events": events or [],
        })
        self._queue.put(("status", status_payload, time.time()))

    def stop(self, join_timeout: float = 2.0):
        self._stop_flag.set()
        self._queue.put(None)  # unblock the worker's get()
        self._worker.join(timeout=join_timeout)

    # --- worker thread --------------------------------------------------

    def _worker_loop(self):
        while not self._stop_flag.is_set():
            item = self._queue.get()
            if item is None:
                break
            command, *payload = item
            if command == "status":
                # payload: (status_payload, enqueue_ts)
                try:
                    status_data = payload[0]
                    enqueue_ts = payload[1] if len(payload) > 1 else None
                except Exception:
                    status_data = payload[0]
                    enqueue_ts = None
                self._post_detection_status(status_data, enqueue_ts)
            elif command == "incident":
                # payload: (alert_type, frame_path, banned_objects_counts, confidence, enqueue_ts)
                if len(payload) >= 5:
                    self._post_incident(payload[0], payload[1], payload[2], payload[3], payload[4])
                elif len(payload) == 4:
                    self._post_incident(payload[0], payload[1], payload[2], payload[3], None)
                elif len(payload) == 3:
                    self._post_incident(payload[0], payload[1], payload[2], None, None)

    def _post_incident(self, alert_type: str, frame_path: str, banned_objects_counts: dict, confidence: float = None, enqueue_ts: float = None):
        dash_type = TYPE_MAP.get(alert_type, "Unknown")
        severity = SEVERITY_MAP.get(alert_type, "medium")

        # Prefer a real confidence supplied by the detection pipeline; only fall
        # back to the per-type map if no value was produced upstream.
        confidence = _normalize_confidence(confidence)
        if confidence is None:
            confidence = CONFIDENCE_MAP.get(alert_type, 0.5)
            confidence = _normalize_confidence(confidence)

        location = self.location
        if alert_type == "object_anomaly" and banned_objects_counts:
            parts = [f"{count} {name}" for name, count in banned_objects_counts.items()]
            location = f"{self.location} ({', '.join(parts)})"

        payload = {
            "camera_id": self.camera_id,
            "detection_type": dash_type,
            "confidence": confidence,
            "severity": severity,
            "status": "Open",
            "location": location,
            "frame_path": frame_path,
        }

        if not self.token and not self._login():
            print(f"[DashboardClient] Dropping {alert_type} incident — not authenticated")
            return

        post_start = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/incidents",
                headers={"Authorization": f"Bearer {self.token}"},
                json=payload,
                timeout=self.request_timeout,
            )
            post_end = time.time()
            # Optional perf logging
            if self.perf_log_path:
                try:
                    self._write_perf_row({
                        "event": "incident",
                        "alert_type": alert_type,
                        "enqueue_ts": enqueue_ts,
                        "post_start_ts": post_start,
                        "post_end_ts": post_end,
                        "http_status": response.status_code,
                        "error": "",
                        "request_elapsed_s": getattr(response.elapsed, "total_seconds", lambda: None)(),
                    })
                except Exception:
                    pass

            if response.status_code == 201:
                print(f"[DashboardClient] Reported {dash_type} ({severity})")
            elif response.status_code == 401:
                # token expired mid-session — re-auth and retry once
                if self._login():
                    self._post_incident(alert_type, frame_path, banned_objects_counts, enqueue_ts)
            else:
                print(f"[DashboardClient] Incident post failed: HTTP {response.status_code} {response.text}")
        except Exception as e:
            post_end = time.time()
            if self.perf_log_path:
                try:
                    self._write_perf_row({
                        "event": "incident",
                        "alert_type": alert_type,
                        "enqueue_ts": enqueue_ts,
                        "post_start_ts": post_start,
                        "post_end_ts": post_end,
                        "http_status": "",
                        "error": str(e),
                        "request_elapsed_s": "",
                    })
                except Exception:
                    pass
            print(f"[DashboardClient] Incident post error: {e}")

    def _post_detection_status(self, status_data: dict, enqueue_ts: float = None):
        """POST live detection status to /api/detections/status (best-effort).

        If `perf_log_path` is set, log timings for each status POST as well.
        """
        if not self.token and not self._login():
            return

        post_start = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/detections/status",
                headers={"Authorization": f"Bearer {self.token}"},
                json=status_data,
                timeout=self.request_timeout,
            )
            post_end = time.time()
            if self.perf_log_path:
                try:
                    self._write_perf_row({
                        "event": "status",
                        "alert_type": "",
                        "enqueue_ts": enqueue_ts,
                        "post_start_ts": post_start,
                        "post_end_ts": post_end,
                        "http_status": response.status_code,
                        "error": "",
                        "request_elapsed_s": getattr(response.elapsed, "total_seconds", lambda: None)(),
                    })
                except Exception:
                    pass

            if response.status_code == 200:
                pass
            elif response.status_code == 401:
                if self._login():
                    self._post_detection_status(status_data, enqueue_ts)
        except Exception:
            post_end = time.time()
            if self.perf_log_path:
                try:
                    self._write_perf_row({
                        "event": "status",
                        "alert_type": "",
                        "enqueue_ts": enqueue_ts,
                        "post_start_ts": post_start,
                        "post_end_ts": post_end,
                        "http_status": "",
                        "error": "exception",
                        "request_elapsed_s": "",
                    })
                except Exception:
                    pass
            # Swallow silently — status push is best-effort and non-critical
            pass

    def _write_perf_row(self, row: dict):
        """Append a performance-measurement row to CSV (create header if needed)."""
        if not self.perf_log_path:
            return
        fieldnames = [
            "ts_logged",
            "event",
            "alert_type",
            "enqueue_ts",
            "post_start_ts",
            "post_end_ts",
            "post_delay_s",
            "request_elapsed_s",
            "http_status",
            "error",
        ]
        try:
            existed = self.perf_log_path.exists()
            with open(self.perf_log_path, "a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames)
                if not existed:
                    writer.writeheader()
                post_start = row.get("post_start_ts") or 0.0
                post_end = row.get("post_end_ts") or 0.0
                writer.writerow({
                    "ts_logged": time.time(),
                    "event": row.get("event", ""),
                    "alert_type": row.get("alert_type", ""),
                    "enqueue_ts": row.get("enqueue_ts", ""),
                    "post_start_ts": post_start,
                    "post_end_ts": post_end,
                    "post_delay_s": (post_end - post_start) if post_end and post_start else "",
                    "request_elapsed_s": row.get("request_elapsed_s", ""),
                    "http_status": row.get("http_status", ""),
                    "error": row.get("error", ""),
                })
        except Exception:
            # Never raise from the perf logger — it's best-effort only.
            pass
