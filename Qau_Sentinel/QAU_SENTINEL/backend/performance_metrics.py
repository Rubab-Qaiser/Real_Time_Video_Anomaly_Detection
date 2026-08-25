import csv
import os
import threading
import time
from collections import deque
from pathlib import Path


class PerformanceMetrics:
    """Thread-safe metrics store for thesis measurements (Socket RTT + inference FPS)."""

    def __init__(self, csv_path: str = None):
        self._lock = threading.Lock()
        self.socket_rtts_ms = deque(maxlen=200)
        self.inference_ms_values = deque(maxlen=200)
        self.last_socket_rtt_ms = 0.0
        self.last_inference_ms = 0.0
        self.last_fps = 0.0

        self.csv_path = Path(csv_path) if csv_path else None
        if self.csv_path:
            try:
                self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

    def record_socket_rtt(self, rtt_ms: float):
        try:
            value = float(rtt_ms)
        except Exception:
            return

        with self._lock:
            self.last_socket_rtt_ms = value
            self.socket_rtts_ms.append(value)
            self._write_csv_row("socket_rtt_ms", value, "")

    def record_inference(self, inference_ms: float):
        try:
            value = float(inference_ms)
        except Exception:
            return

        with self._lock:
            self.last_inference_ms = value
            self.inference_ms_values.append(value)
            fps = 1000.0 / value if value > 0 else 0.0
            self.last_fps = fps
            self._write_csv_row("inference_ms", value, f"{fps:.2f}")

    def get_snapshot(self):
        with self._lock:
            avg_socket = 0.0
            if self.socket_rtts_ms:
                avg_socket = sum(self.socket_rtts_ms) / len(self.socket_rtts_ms)

            avg_inference = 0.0
            if self.inference_ms_values:
                avg_inference = sum(self.inference_ms_values) / len(self.inference_ms_values)

            avg_fps = 1000.0 / avg_inference if avg_inference > 0 else 0.0

            snapshot = {
                "timestamp": time.time(),
                "socket_rtt_ms": round(self.last_socket_rtt_ms, 3),
                "socket_rtt_avg_ms": round(avg_socket, 3),
                "inference_ms": round(self.last_inference_ms, 3),
                "inference_avg_ms": round(avg_inference, 3),
                "fps": round(self.last_fps, 3),
                "fps_avg": round(avg_fps, 3),
            }
            print(f"[THESIS_METRICS] socket_rtt_ms={snapshot['socket_rtt_ms']} | inference_ms={snapshot['inference_ms']} | fps={snapshot['fps']}")
            return snapshot

    def _write_csv_row(self, metric_name: str, metric_value: float, fps_value: str = ""):
        if not self.csv_path:
            return
        try:
            file_exists = self.csv_path.exists()
            with open(self.csv_path, "a", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                if not file_exists:
                    writer.writerow(["timestamp", "metric_name", "metric_value_ms", "fps", "note"])
                writer.writerow([
                    time.time(),
                    metric_name,
                    round(float(metric_value), 6),
                    fps_value,
                    "thesis_metrics",
                ])
        except Exception:
            pass
