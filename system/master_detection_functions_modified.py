"""
master_detection_functions.py

Phase 4.2 + 4.3 + Phase 5.5 (new) — Detection-side building blocks:
    anomalies phase:

    FireSmokeDetector  - runs the fire/smoke YOLOv8n(OpenVINO) model on a
                          background thread, throttled to roughly once
                          every N frames, with debounce to reject flicker.

    CrowdCounter       - Haar Cascade-based head detection (classical CV,
                          no training required) with AREA-BASED assessment:
                          • Maps pixel coordinates to real-world meters
                          • Calculates density (people/m²) per zone
                          • Supports multi-zone thresholds (e.g., entry vs.
                            hallway with different density limits)
                          • Backward-compatible: still supports simple count
                            threshold if no zones defined

    draw_hud_overlay   - draws both signals onto a frame using the same
                          dark glassmorphism palette as the Sentinel
                          frontend (teal / amber / crimson).

CALIBRATION: Three strategies are supported:
  1. Known FOV + ground distance (no manual calibration)
  2. Reference object calibration (most robust)
  3. Simple pixel-ratio calibration (one-time setup)

These are designed to be dropped next to motion_heuristics.py and reuse
the same OpenVINO-model-folder convention produced by train_fire_smoke.py
(a "*_openvino_model" directory containing model.xml / model.bin).
"""

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

import cv2
import numpy as np

# --- Palette, matching the Next.js frontend design tokens -----------------
COLOR_BG = (15, 9, 6)          # #06090F (BGR)
COLOR_TEAL = (181, 240, 0)     # #00F0B5 (BGR)
COLOR_VIOLET = (255, 92, 124)  # #7C5CFF (BGR)
COLOR_AMBER = (32, 176, 255)   # #FFB020 (BGR)
COLOR_CRIMSON = (87, 59, 255)  # #FF3B57 (BGR)


# ---------------------------------------------------------------------------
# Fire / Smoke — throttled background thread
# ---------------------------------------------------------------------------

@dataclass
class FireSmokeStatus:
    fire: bool = False
    smoke: bool = False
    fire_confidence: float = 0.65
    smoke_confidence: float = 0.65
    last_updated: float = 0.0


class FireSmokeDetector:
    """
    Runs a fire/smoke model on its own thread, reading only the most
    recent frame (never a backlog), roughly once every `interval_frames`
    at the given `fps_estimate`. Debounces alerts so a single noisy frame
    (sunset glow, warm indoor lighting) doesn't fire an alert on its own.
    """

    def __init__(
        self,
        model_path: str,
        interval_frames: int = 60,
        fps_estimate: float = 20.0,
        fire_conf_threshold: float = 0.45,
        smoke_conf_threshold: float = 0.8,
        debounce_hits: int = 2,
        history_len: int = 5,
    ):
        from ultralytics import YOLO  # local import: keeps module import light if unused

        self.engine = YOLO(model_path)  # model_path = exported "*_openvino_model" folder
        self.interval_sec = max(interval_frames / fps_estimate, 0.5)
        self.fire_conf_threshold = fire_conf_threshold
        self.smoke_conf_threshold = smoke_conf_threshold
        self.debounce_hits = debounce_hits

        self._latest_frame = None
        self._frame_lock = threading.Lock()

        self._fire_hit_history = deque(maxlen=history_len)
        self._smoke_hit_history = deque(maxlen=history_len)

        self.status = FireSmokeStatus()
        self._status_lock = threading.Lock()

        self._stop_flag = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="FireSmokeDetector")

        # --- Priority throttling (Phase 5) -----------------------------
        # When the main loop signals a high-priority event (e.g. a fall),
        # it can call set_throttle(multiplier) to slow this background
        # thread's polling cadence, freeing CPU/GIL time for the
        # foreground pose/motion pipeline. multiplier=1.0 is normal speed.
        self._throttle_multiplier = 1.0
        self._throttle_lock = threading.Lock()

    def set_throttle(self, multiplier: float):
        """
        Scale the polling interval by `multiplier` (>=1.0 slows down,
        1.0 = normal). Takes effect on the next polling cycle — safe to
        call from the main thread at any time.
        """
        with self._throttle_lock:
            self._throttle_multiplier = max(1.0, multiplier)

    def _current_wait_sec(self) -> float:
        with self._throttle_lock:
            return self.interval_sec * self._throttle_multiplier

    def start(self):
        self._thread.start()
        return self

    def stop(self, join_timeout: float = 2.0):
        self._stop_flag.set()
        self._thread.join(timeout=join_timeout)

    def update_frame(self, frame: np.ndarray):
        """Call this every frame from the main loop. Cheap — just swaps a reference."""
        with self._frame_lock:
            self._latest_frame = frame

    def get_status(self) -> FireSmokeStatus:
        with self._status_lock:
            return FireSmokeStatus(**self.status.__dict__)

    def _run_loop(self):
        while not self._stop_flag.is_set():
            frame = self._grab_latest_frame()
            if frame is not None:
                self._infer_and_update(frame)
            self._stop_flag.wait(self._current_wait_sec())

    def _grab_latest_frame(self):
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def _infer_and_update(self, frame: np.ndarray):
        # engine.predict uses a single conf for early filtering, so we pass the minimum of both
        min_conf = min(self.fire_conf_threshold, self.smoke_conf_threshold)
        results = self.engine.predict(frame, conf=min_conf, verbose=False)[0]

        fire_conf = 0.0
        smoke_conf = 0.0
        for box in results.boxes:
            cls_id = int(box.cls.item())
            conf = float(box.conf.item())
            if cls_id == 0:  # fire
                fire_conf = max(fire_conf, conf)
            elif cls_id == 1:  # smoke
                smoke_conf = max(smoke_conf, conf)

        self._fire_hit_history.append(fire_conf >= self.fire_conf_threshold)
        self._smoke_hit_history.append(smoke_conf >= self.smoke_conf_threshold)

        fire_confirmed = sum(self._fire_hit_history) >= self.debounce_hits
        smoke_confirmed = sum(self._smoke_hit_history) >= self.debounce_hits

        with self._status_lock:
            self.status = FireSmokeStatus(
                fire=fire_confirmed,
                smoke=smoke_confirmed,
                fire_confidence=fire_conf,
                smoke_confidence=smoke_conf,
                last_updated=time.time(),
            )


# ---------------------------------------------------------------------------
# Crowd Counting via Haar Cascade head detection (classical CV)
# ENHANCED: Area-based assessment with multi-zone support (Phase 5.5)
# ---------------------------------------------------------------------------

@dataclass
class ZoneDensity:
    """Per-zone density report."""
    zone_name: str
    head_count: int
    area_m2: float
    density_people_per_m2: float
    threshold_people_per_m2: float
    is_crowded: bool


@dataclass
class CrowdStatus:
    """Enhanced crowd status with area-based metrics."""
    count: int = 0
    raw_count: int = 0
    is_crowd: bool = False
    last_updated: float = 0.0
    method: str = "haar_cascade"  # Track which detector was used

    # NEW: Area-based metrics (Phase 5.5)
    area_m2: Optional[float] = None  # Total detected area (if multi-zone, sum of zones)
    density_people_per_m2: Optional[float] = None  # Overall density
    zone_densities: Optional[List[ZoneDensity]] = None  # Per-zone breakdown
    head_positions_world: Optional[List[Tuple[float, float]]] = None  # World coordinates (mx, my)


class CalibrationConfig:
    """
    Encapsulates calibration parameters for mapping pixel coordinates to
    real-world meters.

    Three strategies are supported:

    1. KNOWN_FOV: Camera specs are known
       - camera_height_m: Height of camera above ground (meters)
       - horizontal_fov_deg: Horizontal field of view (degrees)
       - frame_width_px, frame_height_px: Video resolution

    2. REFERENCE_OBJECT: Calibrate by pointing at known-size object
       - reference_pixel_width: Pixel span of reference object
       - reference_world_width_m: Known real-world size
       - reference_y_px: Vertical position in frame (for perspective adjustment)

    3. SIMPLE_RATIO: Manual pixels-to-meters conversion
       - pixels_per_meter: Scaling factor (updated once during setup)
    """

    def __init__(self, strategy: str = "simple_ratio"):
        self.strategy = strategy  # "known_fov" | "reference_object" | "simple_ratio"

        # Known FOV strategy
        self.camera_height_m: float = 2.5
        self.horizontal_fov_deg: float = 60.0
        self.frame_width_px: int = 640
        self.frame_height_px: int = 480

        # Reference object strategy
        self.reference_pixel_width: int = 100
        self.reference_world_width_m: float = 1.0
        self.reference_y_px: int = 240

        # Simple ratio strategy (fallback)
        self.pixels_per_meter: float = 50.0  # 50 pixels = 1 meter

    def pixel_to_world(self, x_px: float, y_px: float,
                        frame_width: int, frame_height: int) -> Tuple[float, float]:
        """
        Convert pixel coordinates to world meters (x, y) at ground plane.

        Returns: (x_m, y_m) in real-world coordinates
        """
        if self.strategy == "known_fov":
            return self._pixel_to_world_fov(x_px, y_px, frame_width, frame_height)
        elif self.strategy == "reference_object":
            return self._pixel_to_world_reference(x_px, y_px, frame_width, frame_height)
        else:  # simple_ratio
            return self._pixel_to_world_ratio(x_px, y_px)

    def _pixel_to_world_fov(self, x_px: float, y_px: float,
                             frame_width: int, frame_height: int) -> Tuple[float, float]:
        """
        Map pixels to world using camera height and FOV.
        Assumes camera points downward at ground plane.
        """
        # Normalize pixel coords to center, then to sensor angle
        x_norm = (x_px - frame_width / 2.0) / (frame_width / 2.0)
        y_norm = (y_px - frame_height / 2.0) / (frame_height / 2.0)

        # Convert FOV to radians
        fov_rad = np.radians(self.horizontal_fov_deg)

        # Distance from camera to ground point (in meters)
        # Uses small-angle approximation; for steep angles use trigonometry
        x_m = self.camera_height_m * np.tan(x_norm * fov_rad / 2.0)
        y_m = self.camera_height_m * np.tan(y_norm * fov_rad / 2.0)

        return (x_m, y_m)

    def _pixel_to_world_reference(self, x_px: float, y_px: float,
                                   frame_width: int, frame_height: int) -> Tuple[float, float]:
        """
        Map pixels to world using a reference object in the frame.
        Scale is perspective-corrected based on vertical position.
        """
        # Calculate scale at this y_px relative to reference object
        # Closer to reference = more accurate scale
        y_distance = abs(y_px - self.reference_y_px)
        # Simple perspective correction: closer to reference, less distortion
        perspective_factor = 1.0 + (0.05 * y_distance / self.frame_height_px)

        pixels_per_meter = (self.reference_pixel_width / self.reference_world_width_m) * perspective_factor

        # Normalize to center and convert
        x_m = (x_px - frame_width / 2.0) / pixels_per_meter
        y_m = (y_px - self.reference_y_px) / pixels_per_meter

        return (x_m, y_m)

    def _pixel_to_world_ratio(self, x_px: float, y_px: float) -> Tuple[float, float]:
        """
        Simple linear scaling: pixels to meters.
        Assumes uniform scale (no perspective correction).
        """
        x_m = (x_px - self.frame_width_px / 2.0) / self.pixels_per_meter
        y_m = (y_px - self.frame_height_px / 2.0) / self.pixels_per_meter
        return (x_m, y_m)


class CrowdCounter:
    """
    Head-detection based crowd counter using OpenCV's pre-trained
    Haar Cascade classifier. No training required. Fast on CPU.

    ENHANCED (Phase 5.5): Supports area-based crowd assessment with
    multi-zone thresholds and real-world density calculation.

    Dataset-informed thresholds (1280x720 reference resolution):
      - RWF-2000 violent crowds: 15–45 people per frame
      - UCF-Crime crowd scenes: 10–30 people typical, 25+ is anomalous
      - Recommendation (count-based): density_threshold = 18 (conservative)

    NEW Density-based thresholds (area-aware):
      - Low-density zone (e.g., reception): 1.5–2.0 people/m²
      - Medium-density zone (e.g., hallway): 2.5–3.0 people/m²
      - High-density zone (e.g., elevator): 3.5–4.5 people/m²

    The count is smoothed via a rolling window to suppress frame-to-frame jitter.
    Unlike fire/smoke, crowd density can shift frame-to-frame, so this runs
    on a much shorter cadence (every `interval_frames`, default every ~8
    frames / 2-4Hz at 20fps) rather than a background thread — it's cheap
    enough to run inline.
    """

    def __init__(
        self,
        cascade_path: str = None,
        interval_frames: int = 8,
        density_threshold: int = 8,
        smoothing_window: int = 5,
        scale_factor: float = 1.1,
        min_neighbors: int = 3,
        min_size: tuple = (30, 30),
        max_size: tuple = (150, 150),
        calibration: Optional["CalibrationConfig"] = None,
        zones: Optional[List[Dict]] = None,
    ):
        """
        Args:
            cascade_path: Path to Haar Cascade XML. If None, uses OpenCV's default.
            interval_frames: Run inference every N frames (8 ≈ 2–4Hz at 20fps).
            density_threshold: Head count threshold for crowd anomaly.
                               Dataset-informed: 15–25 depending on resolution & dataset.
            smoothing_window: Rolling average window size.
            scale_factor: Haar Cascade parameter (lower = slower but more sensitive).
            min_neighbors: Cascade voting threshold (higher = fewer false positives).
            min_size, max_size: Bounding box constraints for detected heads.
            calibration: CalibrationConfig for pixel→meter conversion. If None, count-based only.
            zones: List of zone dicts with keys:
                   - "name" (str): Zone identifier
                   - "area_m2" (float): Real-world area
                   - "density_threshold" (float): People per m²
                   - "pixel_bounds" ((x1, y1, x2, y2)): Pixel rectangle in frame
        """
        if cascade_path is None:
            # Use OpenCV's pre-trained frontal face cascade; works for head detection in many contexts
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

        self.cascade = cv2.CascadeClassifier(cascade_path)
        if self.cascade.empty():
            raise ValueError(f"Failed to load Haar Cascade from {cascade_path}")

        self.interval_frames = interval_frames
        self.density_threshold = density_threshold
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        self.max_size = max_size

        self.calibration = calibration or CalibrationConfig(strategy="simple_ratio")
        self.zones = zones or []

        self._frame_count = 0
        self._history = deque(maxlen=smoothing_window)
        self.status = CrowdStatus()
        self._last_boxes = []  # kept for overlay drawing between inference ticks

    def process(self, frame: np.ndarray) -> CrowdStatus:
        """Call every frame. Internally only runs inference every N frames."""
        self._frame_count += 1
        if self._frame_count % self.interval_frames == 0:
            self._infer(frame)
        return self.status

    def _infer(self, frame: np.ndarray):
        """
        Run Haar Cascade detection on the frame.
        Convert to grayscale for better performance (Haar Cascades work on intensity).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Equalize histogram for better detection in varied lighting
        gray = cv2.equalizeHist(gray)

        boxes = self.cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
            maxSize=self.max_size,
        )

        # Convert from (x, y, w, h) to (x1, y1, x2, y2)
        detected_boxes = []
        head_positions_px = []
        for (x, y, w, h) in boxes:
            x1, y1, x2, y2 = x, y, x + w, y + h
            detected_boxes.append([x1, y1, x2, y2])
            # Store head center in pixel coords
            head_x_px = (x1 + x2) / 2.0
            head_y_px = (y1 + y2) / 2.0
            head_positions_px.append((head_x_px, head_y_px))

        self._last_boxes = detected_boxes

        raw_count = len(boxes)
        self._history.append(raw_count)
        smoothed = round(sum(self._history) / len(self._history))

        # Calculate area-based metrics if calibration is configured
        head_positions_world = None
        zone_densities = None
        overall_area_m2 = None
        overall_density = None
        is_crowd = smoothed >= self.density_threshold  # Default: count-based

        if self.calibration:
            h, w = frame.shape[:2]
            head_positions_world = []
            for x_px, y_px in head_positions_px:
                x_m, y_m = self.calibration.pixel_to_world(x_px, y_px, w, h)
                head_positions_world.append((x_m, y_m))

            # If zones are defined, compute per-zone density
            if self.zones:
                zone_densities = []
                total_area = 0.0
                total_heads_in_zones = 0

                for zone in self.zones:
                    zone_name = zone.get("name", "unnamed")
                    area_m2 = zone.get("area_m2", 1.0)
                    threshold = zone.get("density_threshold", 2.5)
                    x1, y1, x2, y2 = zone.get("pixel_bounds", (0, 0, w, h))

                    # Count heads in this zone
                    heads_in_zone = 0
                    for x_px, y_px in head_positions_px:
                        if x1 <= x_px <= x2 and y1 <= y_px <= y2:
                            heads_in_zone += 1

                    density = heads_in_zone / area_m2 if area_m2 > 0 else 0.0
                    is_zone_crowded = density >= threshold

                    zone_densities.append(ZoneDensity(
                        zone_name=zone_name,
                        head_count=heads_in_zone,
                        area_m2=area_m2,
                        density_people_per_m2=density,
                        threshold_people_per_m2=threshold,
                        is_crowded=is_zone_crowded,
                    ))

                    total_area += area_m2
                    total_heads_in_zones += heads_in_zone

                # Overall crowd flag: True if ANY zone exceeds its threshold
                is_crowd = any(zd.is_crowded for zd in zone_densities)
                overall_area_m2 = total_area if total_area > 0 else None
                overall_density = (total_heads_in_zones / total_area
                                   if total_area > 0 else None)
            else:
                # No zones: use calibration to compute overall density
                # Assume the entire frame is the detection area (user must set this)
                # For now, fall back to count-based threshold
                pass

        self.status = CrowdStatus(
            count=smoothed,
            raw_count=raw_count,
            is_crowd=is_crowd,
            last_updated=time.time(),
            method="haar_cascade",
            area_m2=overall_area_m2,
            density_people_per_m2=overall_density,
            zone_densities=zone_densities,
            head_positions_world=head_positions_world,
        )

    def get_last_head_boxes(self):
        """Boxes from the most recent inference tick, for overlay drawing."""
        return self._last_boxes

    def update_calibration(self, calibration: "CalibrationConfig"):
        """Update calibration parameters on-the-fly."""
        self.calibration = calibration

    def update_zones(self, zones: List[Dict]):
        """Update zone definitions on-the-fly."""
        self.zones = zones


# ---------------------------------------------------------------------------
# Overlay drawing helpers
# ---------------------------------------------------------------------------

def draw_head_boxes(frame: np.ndarray, boxes, color=COLOR_TEAL):
    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 1)
    return frame


def draw_zones_overlay(frame: np.ndarray, zones: Optional[List[Dict]],
                        zone_densities: Optional[List[ZoneDensity]] = None,
                        thickness: int = 2):
    """
    Draw zone boundaries and density info on frame.

    Args:
        frame: The video frame.
        zones: List of zone dicts (must have "pixel_bounds" and "name").
        zone_densities: Optional list of ZoneDensity results from crowd detection.
        thickness: Line thickness for zone rectangles.
    """
    if not zones:
        return frame

    density_map = {}
    if zone_densities:
        for zd in zone_densities:
            density_map[zd.zone_name] = zd

    for zone in zones:
        name = zone.get("name", "unnamed")
        x1, y1, x2, y2 = zone.get("pixel_bounds", (0, 0, frame.shape[1], frame.shape[0]))
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        zd = density_map.get(name)
        if zd is not None:
            color = COLOR_CRIMSON if zd.is_crowded else COLOR_TEAL
            label = f"{name}: {zd.density_people_per_m2:.2f}/{zd.threshold_people_per_m2:.2f} p/m2"
        else:
            color = COLOR_VIOLET
            label = name

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        label_y = y1 - 8 if y1 - 8 > 10 else y1 + 18
        cv2.putText(frame, label, (x1, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    return frame


def draw_hud_overlay(frame: np.ndarray, fire_smoke_status: FireSmokeStatus,
                      crowd_status: CrowdStatus,
                      crowd_density_threshold: int = 18,
                      show_area_metrics: bool = True):
    """
    Draws a small HUD panel in the top-left: fire/smoke state and crowd
    count, colored teal/amber/crimson to match the Sentinel frontend.

    If show_area_metrics=True and crowd_status has density info, displays
    density instead of raw count.
    """
    h, w = frame.shape[:2]
    panel_w, panel_h = 260, 90
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (10 + panel_w, 10 + panel_h), COLOR_BG, -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    def status_color(active: bool):
        return COLOR_CRIMSON if active else COLOR_TEAL

    fire_text = f"FIRE: {'ALERT' if fire_smoke_status.fire else 'clear'} ({fire_smoke_status.fire_confidence:.2f})"
    smoke_text = f"SMOKE: {'ALERT' if fire_smoke_status.smoke else 'clear'} ({fire_smoke_status.smoke_confidence:.2f})"

    approaching_threshold = int(0.7 * max(1, crowd_density_threshold))
    if crowd_status.is_crowd:
        crowd_color = COLOR_CRIMSON
    elif crowd_status.count >= approaching_threshold:
        crowd_color = COLOR_AMBER
    else:
        crowd_color = COLOR_TEAL
    method_abbr = "HAR" if crowd_status.method == "haar_cascade" else crowd_status.method[:3].upper()

    # Build crowd text: count-based or area-based
    if show_area_metrics and crowd_status.density_people_per_m2 is not None:
        crowd_text = f"DENSITY: {crowd_status.density_people_per_m2:.2f} p/m² [{method_abbr}]"
    else:
        crowd_text = f"HEADS: {crowd_status.count} [{method_abbr}]"

    cv2.putText(frame, fire_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color(fire_smoke_status.fire), 2)
    cv2.putText(frame, smoke_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color(fire_smoke_status.smoke), 2)
    cv2.putText(frame, crowd_text, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.55, crowd_color, 2)

    return frame


# ---------------------------------------------------------------------------
# Live MJPEG streaming (Phase 5.4) — for the Next.js dashboard's video panel
# ---------------------------------------------------------------------------
#
# Design note: the main loop already owns the one and only cv2.VideoCapture
# and already produces a fully-annotated frame every iteration (pose boxes +
# HUD + alert flashing). Rather than opening a second VideoCapture inside
# this Flask app (which fights the main loop for the camera device and
# doubles CPU load), this broadcaster just holds a reference to the *latest
# annotated frame* and re-encodes it to JPEG on demand for each connected
# client. The main loop calls `broadcaster.update(annotated)` once per
# frame; everything else runs on a background thread.

class FrameBroadcaster:
    """Thread-safe holder for the most recent annotated frame."""

    def __init__(self, jpeg_quality: int = 80):
        self._frame = None
        self._lock = threading.Lock()
        self._jpeg_quality = jpeg_quality

    def update(self, frame: np.ndarray):
        """Call once per iteration of the main loop with the annotated frame."""
        with self._lock:
            self._frame = frame

    def get_jpeg(self):
        """Returns encoded JPEG bytes for the latest frame, or None if no frame yet."""
        with self._lock:
            frame = None if self._frame is None else self._frame.copy()
        if frame is None:
            return None
        ok, buffer = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self._jpeg_quality]
        )
        if not ok:
            return None
        return buffer.tobytes()


def start_stream_server(broadcaster: "FrameBroadcaster", host: str = "0.0.0.0",
                         port: int = 8080, target_fps: float = 15.0):
    """
    Starts a small Flask MJPEG server on a daemon background thread and
    returns the thread. Does NOT open its own camera — it only ever reads
    frames that the main loop has pushed via `broadcaster.update(frame)`.

    Frontend/dashboard can point an <img> tag straight at:
        http://<this-machine-ip>:{port}/stream
    """
    from flask import Flask, Response

    app = Flask(__name__)
    min_interval = 1.0 / target_fps

    def generate_frames():
        while True:
            start = time.time()
            jpeg = broadcaster.get_jpeg()
            if jpeg is not None:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")
            elapsed = time.time() - start
            time.sleep(max(0.0, min_interval - elapsed))

    @app.route("/stream")
    def stream():
        return Response(generate_frames(),
                         mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.route("/health")
    def health():
        return {"status": "ok", "has_frame": broadcaster.get_jpeg() is not None}

    def _run():
        # use_reloader must stay False: it's off by default outside __main__,
        # but pinning it explicitly avoids Flask trying to fork this thread.
        app.run(host=host, port=port, threaded=True, use_reloader=False)

    thread = threading.Thread(target=_run, daemon=True, name="MJPEGStreamServer")
    thread.start()
    print(f"[FrameBroadcaster] MJPEG stream live at http://{host}:{port}/stream")
    return thread