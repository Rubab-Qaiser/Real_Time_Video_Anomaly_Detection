"""
master_mega_alerts.py

Phase 5.3 — Unified Visual alert triggers for the Mega Dashboard.
Integrates Object Anomaly tracking (banned classes).
"""
import os
import time
from dataclasses import dataclass

import cv2
import numpy as np

COLOR_CRIMSON = (87, 59, 255)   # #FF3B57 (BGR)
COLOR_WHITE = (255, 255, 255)

FLASH_HZ = 4.0

LOCALIZED_TYPES = {"fall", "fight", "running"}
WIDE_TYPES = {"fire", "smoke", "crowd", "object_anomaly"}

@dataclass
class AlertEvent:
    alert_type: str
    timestamp: float
    frame_path: str = ""

class MegaAlertManager:
    def __init__(
        self,
        alerts_dir: str = "Alerts",
        log_cooldown_sec: float = 2.0,
        flash_hz: float = FLASH_HZ,
        on_alert=None,
    ):
        self.alerts_dir = alerts_dir
        self.log_cooldown_sec = log_cooldown_sec
        self.flash_hz = flash_hz
        # Optional callback: on_alert(alert_type: str, frame_path: str, banned_objects_counts: dict)
        # Fired from maybe_log(), i.e. already de-duplicated by log_cooldown_sec —
        # this is the single hook point for pushing incidents to an external
        # dashboard/API without the main loop needing to know about it.
        self.on_alert = on_alert

        os.makedirs(self.alerts_dir, exist_ok=True)

        self._last_logged_at = {}
        self._person_events = []
        self._wide_types = set()
        self._active_types = set()
        self._type_confidences = {}
        self.history = []

        # New for object anomalies
        self._banned_objects_counts = {}

    def update(self, person_events: list, wide_types: set, banned_objects_counts: dict = None):
        """
        person_events: list of (bbox, types) tuples
        wide_types: set of frame-wide anomalies (fire, smoke, crowd, object_anomaly)
        banned_objects_counts: dictionary like {"bicycle": 3, "car": 1}
        """
        self._person_events = [(bbox, set(types) & LOCALIZED_TYPES) for bbox, types in person_events]
        self._wide_types = set(wide_types) & WIDE_TYPES
        self._active_types = self._wide_types | {t for _, types in self._person_events for t in types}
        
        if banned_objects_counts:
            self._banned_objects_counts = banned_objects_counts
        else:
            self._banned_objects_counts = {}

    @property
    def is_active(self) -> bool:
        return len(self._active_types) > 0

    def _flash_on(self) -> bool:
        return int(time.time() * self.flash_hz * 2) % 2 == 0

    def draw(self, frame: np.ndarray) -> np.ndarray:
        if not self.is_active:
            return frame

        if not self._flash_on():
            return frame

        # Draw localized boxes
        for bbox, types in self._person_events:
            if not types:
                continue
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), COLOR_CRIMSON, 4)
            label = "/".join(sorted(t.upper() for t in types))
            cv2.putText(frame, label, (int(x1), max(0, int(y1) - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_CRIMSON, 2)

        # Draw full-frame border
        if self._wide_types:
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), COLOR_CRIMSON, 10)

        # Format label
        labels_to_draw = []
        for t in sorted(self._active_types):
            if t == "object_anomaly" and self._banned_objects_counts:
                # Format: OBJECT ANOMALY (3 bicycles, 1 car)
                parts = []
                for obj_name, count in self._banned_objects_counts.items():
                    plural = "s" if count > 1 and not obj_name.endswith('s') else ""
                    parts.append(f"{count} {obj_name}{plural}")
                labels_to_draw.append(f"OBJECT ANOMALY ({', '.join(parts)})")
            else:
                labels_to_draw.append(t.upper())

        label = "  |  ".join(labels_to_draw)
        cv2.putText(frame, f"ALERT: {label}", (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2)
        cv2.putText(frame, f"ALERT: {label}", (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_CRIMSON, 1)

        return frame

    def maybe_log(self, frame: np.ndarray):
        now = time.time()
        for alert_type in self._active_types:
            last = self._last_logged_at.get(alert_type, 0.0)
            if now - last < self.log_cooldown_sec:
                continue

            self._last_logged_at[alert_type] = now
            stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(now))
            ms = int((now % 1) * 1000)
            filename = f"{alert_type}_{stamp}_{ms:03d}.png"
            path = os.path.join(self.alerts_dir, filename)

            cv2.imwrite(path, frame)
            self.history.append(AlertEvent(alert_type=alert_type, timestamp=now, frame_path=path))
            print(f"[MegaAlertManager] Logged {alert_type} incident -> {path}")

            # Deliver optional confidence if available via _type_confidences mapping.
            confidence = None
            try:
                confidence = getattr(self, "_type_confidences", {}).get(alert_type)
                if confidence is not None:
                    confidence = float(confidence)
                    if confidence <= 1.0:
                        confidence *= 100.0
                    confidence = max(0.0, min(100.0, confidence))
            except Exception:
                confidence = None

            if self.on_alert is not None:
                try:
                    # Keep backward compatibility: callers that accept 3 args will
                    # ignore the extra `confidence` parameter.
                    self.on_alert(alert_type, path, dict(self._banned_objects_counts), confidence)
                except TypeError:
                    # Older callbacks: try without confidence arg
                    try:
                        self.on_alert(alert_type, path, dict(self._banned_objects_counts))
                    except Exception as e:
                        print(f"[MegaAlertManager] on_alert callback failed: {e}")
                except Exception as e:
                    # Never let a dashboard/network failure take down the detection loop.
                    print(f"[MegaAlertManager] on_alert callback failed: {e}")
