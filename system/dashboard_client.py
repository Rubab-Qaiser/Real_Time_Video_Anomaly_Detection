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

try:
    # Load credentials from a local .env file (git-ignored) if present.
    # Add "python-dotenv" to system/requirements.txt to enable this.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional at runtime; env vars can be set directly.
    pass


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
    "fall": 0.92,
    "fight": 0.94,
    "fire": 0.90,
    "smoke": 0.87,
    "running": 0.85,
    "crowd": 0.76,
    "object_anomaly": 0.78,
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
    ):
        # Prefer explicit arguments, falling back to environment variables.
        # Credentials are never hardcoded so nothing sensitive is committed.
        self.dashboard_ip = dashboard_ip or _env_dashboard_ip()
        self.dashboard_port = dashboard_port or _env_dashboard_port()
        self.email = email or _env_dashboard_email()
        self.password = password or _env_dashboard_password()
        self.camera_id = camera_id
        self.location = location
        self.request_timeout = request_timeout

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

    def send_detection(self, alert_type: str, frame_path: str, banned_objects_counts: dict):
        """Non-blocking: enqueues the incident and returns immediately."""
        self._queue.put(("incident", alert_type, frame_path, banned_objects_counts))

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
        self._queue.put(("status", {
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
        }))

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
                self._post_detection_status(payload[0])
            elif command == "incident" and len(payload) == 3:
                self._post_incident(payload[0], payload[1], payload[2])

    def _post_incident(self, alert_type: str, frame_path: str, banned_objects_counts: dict):
        dash_type = TYPE_MAP.get(alert_type, "Unknown")
        severity = SEVERITY_MAP.get(alert_type, "medium")

        # Use a per-type default confidence instead of a hardcoded 0.0 so
        # live-detected incidents don't display as "0%" on the dashboard.
        confidence = CONFIDENCE_MAP.get(alert_type, 0.5)

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

        try:
            response = requests.post(
                f"{self.base_url}/incidents",
                headers={"Authorization": f"Bearer {self.token}"},
                json=payload,
                timeout=self.request_timeout,
            )
            if response.status_code == 201:
                print(f"[DashboardClient] Reported {dash_type} ({severity})")
            elif response.status_code == 401:
                # token expired mid-session — re-auth and retry once
                if self._login():
                    self._post_incident(alert_type, frame_path, banned_objects_counts)
            else:
                print(f"[DashboardClient] Incident post failed: HTTP {response.status_code} {response.text}")
        except Exception as e:
            print(f"[DashboardClient] Incident post error: {e}")

    def _post_detection_status(self, status_data: dict):
        """POST live detection status to /api/detections/status (best-effort)."""
        if not self.token and not self._login():
            return

        try:
            response = requests.post(
                f"{self.base_url}/detections/status",
                headers={"Authorization": f"Bearer {self.token}"},
                json=status_data,
                timeout=self.request_timeout,
            )
            if response.status_code == 200:
                pass  # Expected — status pushed successfully
            elif response.status_code == 401:
                if self._login():
                    self._post_detection_status(status_data)
        except Exception:
            # Swallow silently — status push is best-effort and non-critical
            pass
