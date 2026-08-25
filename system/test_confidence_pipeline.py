import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_client import DashboardClient
from master_mega_alerts import MegaAlertManager


class DummyResponse:
    def __init__(self, status_code=201, text="ok"):
        self.status_code = status_code
        self.text = text
        self.elapsed = type("Elapsed", (), {"total_seconds": lambda self: 0.0})()


def test_post_incident_uses_real_confidence(monkeypatch):
    client = DashboardClient.__new__(DashboardClient)
    client.token = "token"
    client.camera_id = 1
    client.location = "Main Entrance"
    client.base_url = "http://example.test/api"
    client.request_timeout = 5.0
    client.perf_log_path = None
    client._login = lambda: True

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return DummyResponse()

    monkeypatch.setattr("dashboard_client.requests.post", fake_post)

    client._post_incident("object_anomaly", "frame.png", {"car": 1}, 0.91, None)

    assert captured["json"]["confidence"] == 91.0
    assert captured["json"]["detection_type"] == "Unwanted Object"


def test_meg_alert_manager_preserves_type_confidences():
    manager = MegaAlertManager(alerts_dir="Alerts", log_cooldown_sec=0.0)
    manager._active_types = {"object_anomaly"}
    manager._type_confidences = {"object_anomaly": 0.91}
    manager._banned_objects_counts = {"car": 1}
    manager._last_logged_at = {}

    seen = {}

    def fake_callback(alert_type, frame_path, banned_objects_counts, confidence):
        seen["alert_type"] = alert_type
        seen["confidence"] = confidence
        seen["counts"] = banned_objects_counts

    manager.on_alert = fake_callback

    # create an actual file so the pipeline does not fail at cv2.imwrite
    import cv2
    import numpy as np

    dummy = np.zeros((10, 10, 3), dtype=np.uint8)
    manager.maybe_log(dummy)

    assert seen["alert_type"] == "object_anomaly"
    assert seen["confidence"] == 91.0
    assert seen["counts"] == {"car": 1}
