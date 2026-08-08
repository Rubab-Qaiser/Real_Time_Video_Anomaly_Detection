"""
master_mega_dashboard.py (v5.3.1 Updated for Specification-Aligned Motion Heuristics)

Phase 5.3 — The Mega Dashboard
Combines:
  1. YOLO-Pose (Full speed) for fall/fight/running.
  2. YOLO-Object (Interleaved/Time-Sliced) for crowd counting and banned object anomalies.
  3. YOLO-Fire/Smoke (Background thread).
  4. MegaAlertManager (flashing boxes, screenshots, object anomaly counts).

Updates for motion_heuristics_2_updated.py:
  - Handles new check_fight() return value: (status, overlap, confidence)
  - Event state visualization (IDLE→CANDIDATE→CONFIRMED→RECOVERY)
  - Enhanced debug metrics from debug_signals()
  - Improved alert logic with state awareness
"""

import argparse
import itertools
import time
from pathlib import Path

import cv2
import numpy as np

from master_detection_functions_modified import (
    FireSmokeDetector,
    FireSmokeStatus,
    CrowdStatus,
    draw_hud_overlay,
    FrameBroadcaster,
    start_stream_server,
)
from master_mega_alerts import MegaAlertManager
from motion_heuristics_Fall_modified import PersonTrack, check_fight
from dashboard_client import DashboardClient

# --- Priority throttling tuning ---------------------------------------
PRIORITY_THROTTLE_MULTIPLIER = 3.0
PRIORITY_RELEASE_COOLDOWN_SEC = 2.0

# --- Track lifecycle ----------------------------------------------------
STALE_TRACK_TIMEOUT_SEC = 3.0

# --- Anomaly panel tuning -----------------------------------------------
PANEL_WIDTH = 300
PANEL_MARGIN = 10
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_POSE_MODEL = BASE_DIR / "yolov8n-pose_openvino_model"
DEFAULT_OBJECT_MODEL = BASE_DIR / "yolo11n_openvino_model_320"
DEFAULT_FIRE_SMOKE_MODEL = BASE_DIR / "fire_smoke_openvino_model" / "venv" / "FireSmokeInference" / "FireSmokeInference" / "fire_smoke_best_openvino_model"


def parse_args():
    parser = argparse.ArgumentParser(description="Phase 5.3 Sentinel Mega Dashboard (Updated)")
    parser.add_argument("--pose-model", default=str(DEFAULT_POSE_MODEL))
    parser.add_argument("--object-model", default=str(DEFAULT_OBJECT_MODEL),
                         help="Path to general YOLO object detection model (for crowds and anomalies)")
    parser.add_argument("--fire-smoke-model", default=str(DEFAULT_FIRE_SMOKE_MODEL),
                         help="Path to exported fire/smoke OpenVINO model folder")
    parser.add_argument("--source", type=str, default="0",
                         help="Webcam source index or path to a video file")
    parser.add_argument("--fps-estimate", type=float, default=10.0,
                         help="Estimated FPS for model configuration")
    parser.add_argument("--frame-skip", type=int, default=3,
                         help="Run heavy object detection every Nth frame")

    # Thresholds
    parser.add_argument("--fire-smoke-interval-frames", type=int, default=60)
    parser.add_argument("--fire-conf-threshold", type=float, default=0.5)
    parser.add_argument("--smoke-conf-threshold", type=float, default=0.8)
    parser.add_argument("--fire-smoke-debounce-hits", type=int, default=2)
    parser.add_argument("--fire-smoke-history-len", type=int, default=5)

    parser.add_argument("--crowd-density-threshold", type=int, default=18)
    parser.add_argument("--alerts-dir", default="Alerts")
    parser.add_argument("--alert-log-cooldown", type=float, default=5.0)
    parser.add_argument("--display-width", type=int, default=960)

    parser.add_argument("--show-anomaly-panel", action="store_true", default=True,
                         help="Display the anomaly score panel (FPS + all six anomaly scores)")
    parser.add_argument("--panel-side", type=str, default="right",
                         choices=["left", "right"],
                         help="Which side of the screen the anomaly panel docks to")

    # --- Live MJPEG stream (for the Next.js dashboard's video panel) ---
    parser.add_argument("--enable-stream", action="store_true", default=True,
                         help="Serve the annotated feed over MJPEG at /stream")
    parser.add_argument("--stream-port", type=int, default=8080)

# --- QAU Sentinel dashboard API integration ---
    parser.add_argument("--enable-dashboard", action="store_true", default=True,
                         help="POST incidents to the Sentinel FastAPI backend")
    parser.add_argument("--dashboard-ip", type=str, default="127.0.0.1",
                         help="IP of the machine running the Sentinel FastAPI backend")
    parser.add_argument("--dashboard-port", type=int, default=5000)
    parser.add_argument("--camera-id", type=int, default=1)
    parser.add_argument("--camera-location", type=str, default="Main Entrance")

    return parser.parse_args()


class PriorityController:
    """
    Manages fire/smoke detector throttling based on high-priority events (fall, fight).
    When priority events detected, increases fire/smoke detection frequency.
    """
    def __init__(self, fire_smoke_detector, throttle_multiplier=PRIORITY_THROTTLE_MULTIPLIER,
                 release_cooldown_sec=PRIORITY_RELEASE_COOLDOWN_SEC):
        self.fire_smoke_detector = fire_smoke_detector
        self.throttle_multiplier = throttle_multiplier
        self.release_cooldown_sec = release_cooldown_sec
        self._throttled = False
        self._last_priority_seen = 0.0

    def update(self, priority_active: bool):
        if self.fire_smoke_detector is None:
            return
        now = time.time()
        if priority_active:
            self._last_priority_seen = now
            if not self._throttled:
                self.fire_smoke_detector.set_throttle(self.throttle_multiplier)
                self._throttled = True
        else:
            if self._throttled and (now - self._last_priority_seen) >= self.release_cooldown_sec:
                self.fire_smoke_detector.set_throttle(1.0)
                self._throttled = False


class PersonTrackManager:
    """
    Manages lifecycle of person tracks from YOLO-Pose.
    Creates PersonTrack instances, updates them with new pose data,
    and evicts stale tracks after timeout.
    """
    def __init__(self, stale_timeout_sec=STALE_TRACK_TIMEOUT_SEC):
        self.stale_timeout_sec = stale_timeout_sec
        self._tracks = {}
        self._last_seen = {}

    def update(self, pose_results):
        now = time.time()
        visible = {}

        boxes = getattr(pose_results, "boxes", None)
        keypoints = getattr(pose_results, "keypoints", None)
        if boxes is None or keypoints is None or boxes.id is None:
            self._evict_stale(now)
            return visible

        ids = boxes.id.int().tolist()
        xyxy = boxes.xyxy.tolist()
        kpts = keypoints.data.cpu().numpy()

        for i, track_id in enumerate(ids):
            track = self._tracks.get(track_id)
            if track is None:
                track = PersonTrack(track_id)
                self._tracks[track_id] = track

            track.update(kpts[i], xyxy[i])
            self._last_seen[track_id] = now
            visible[track_id] = track

        self._evict_stale(now)
        return visible

    def _evict_stale(self, now):
        stale_ids = [tid for tid, ts in self._last_seen.items() if now - ts > self.stale_timeout_sec]
        for tid in stale_ids:
            self._tracks.pop(tid, None)
            self._last_seen.pop(tid, None)


def _status_color(score):
    """Green / orange / red ramp for a 0.0-1.0 severity score."""
    if score >= 0.75:
        return (0, 0, 255)      # Red (BGR)
    if score >= 0.35:
        return (0, 165, 255)    # Orange
    return (0, 210, 90)         # Green


def _draw_score_row(frame, x, y, row_width, label, score, value_text):
    """
    One clean row: LABEL ......... bar ......... value
    Everything lines up on fixed columns so the whole panel reads as a grid,
    not a wall of loose text.
    """
    color = _status_color(score)
    label_x = x
    bar_x = x + 92
    bar_w = 110
    value_x = bar_x + bar_w + 10

    cv2.circle(frame, (x + 4, y - 4), 4, color, -1)
    cv2.putText(frame, label, (label_x + 14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)

    # Bar track + fill
    cv2.rectangle(frame, (bar_x, y - 9), (bar_x + bar_w, y - 1), (70, 70, 70), 1)
    fill_w = int(bar_w * max(0.0, min(1.0, score)))
    if fill_w > 0:
        cv2.rectangle(frame, (bar_x, y - 9), (bar_x + fill_w, y - 1), color, -1)

    cv2.putText(frame, value_text, (value_x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)


def draw_anomaly_score_panel(frame, scores, fps, side="right", panel_width=PANEL_WIDTH):
    """
    Draw one clean, docked anomaly panel — FPS plus all six anomaly scores,
    each as a label + severity bar + value. No scattered text elsewhere on
    the frame; this panel is the single source of truth for scene status.

    scores: ordered list of (label, score_0_to_1, value_text) tuples,
            e.g. [("FALL", 1.0, "1 confirmed"), ("FIRE", 0.0, "clear"), ...]
    side:   "left" or "right" — which edge the panel docks to
    """
    h, w = frame.shape[:2]
    row_height = 26
    top_pad, title_block, bottom_pad = 14, 40, 12
    panel_height = top_pad + title_block + len(scores) * row_height + bottom_pad

    x = PANEL_MARGIN if side == "left" else w - panel_width - PANEL_MARGIN
    y = PANEL_MARGIN

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + panel_width, y + panel_height), (18, 18, 18), -1)
    frame = cv2.addWeighted(overlay, 0.72, frame, 0.28, 0)
    cv2.rectangle(frame, (x, y), (x + panel_width, y + panel_height), (0, 210, 90), 1)

    text_x = x + 14
    line_y = y + 24
    cv2.putText(frame, "SENTINEL", (text_x, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 210, 90), 2)

    fps_color = (0, 210, 90) if fps > 7 else (0, 165, 255) if fps > 4 else (0, 0, 255)
    fps_text = f"{fps:.1f} FPS"
    (fps_w, _), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.putText(frame, fps_text, (x + panel_width - fps_w - 14, line_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, fps_color, 1)

    line_y += 12
    cv2.line(frame, (text_x, line_y), (x + panel_width - 14, line_y), (70, 70, 70), 1)
    line_y += 22

    for label, score, value_text in scores:
        _draw_score_row(frame, text_x, line_y, panel_width - 28, label, score, value_text)
        line_y += row_height

    return frame


def main():
    args = parse_args()

    if args.source is None:
        print("\n=== Video Source Selection ===")
        print("0: Integrated webcam")
        print("1: Iriun webcam")
        print("2: USB connected camera")
        print("Or enter the full path to a recorded video file.")
        user_choice = input("Enter your choice [default: 0]: ").strip()
        args.source = user_choice if user_choice else "0"

    from ultralytics import YOLO

    print("[MegaDashboard] Loading YOLO-Pose...")
    pose_model = YOLO(args.pose_model)

    print("[MegaDashboard] Loading YOLO-Object (Interleaved)...")
    object_model = YOLO(args.object_model)

    fire_smoke_detector = None
    if args.fire_smoke_model:
        fire_smoke_detector = FireSmokeDetector(
            model_path=args.fire_smoke_model,
            interval_frames=args.fire_smoke_interval_frames,
            fps_estimate=args.fps_estimate,
            fire_conf_threshold=args.fire_conf_threshold,
            smoke_conf_threshold=args.smoke_conf_threshold,
            debounce_hits=args.fire_smoke_debounce_hits,
            history_len=args.fire_smoke_history_len,
        ).start()

    dashboard_client = None
    if args.enable_dashboard:
        print(f"[MegaDashboard] Connecting to dashboard at {args.dashboard_ip}:{args.dashboard_port}...")
        dashboard_client = DashboardClient(
            dashboard_ip=args.dashboard_ip,
            dashboard_port=args.dashboard_port,
            camera_id=args.camera_id,
            location=args.camera_location,
        )

    alert_manager = MegaAlertManager(
        alerts_dir=args.alerts_dir,
        log_cooldown_sec=args.alert_log_cooldown,
        on_alert=dashboard_client.send_detection if dashboard_client else None,
    )
    priority_controller = PriorityController(fire_smoke_detector)
    track_manager = PersonTrackManager()

    frame_broadcaster = None
    if args.enable_stream:
        frame_broadcaster = FrameBroadcaster()
        start_stream_server(frame_broadcaster, port=args.stream_port)

    source = args.source
    if source.isdigit():
        source = int(source)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source {args.source}")

    # Banned classes for Object Anomaly
    # 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
    BANNED_CLASS_IDS = {1, 2, 3, 5, 7}

    # Caches for Time-Slicing the Object Detection
    cached_banned_counts = {}
    cached_banned_boxes = []  # [(x1,y1,x2,y2, label)]
    cached_crowd_status = CrowdStatus()
    cached_people_boxes = []

    frame_idx = 0
    frame_times = []
    _status_push_counter = 0          # Throttle dashboard status push
    _STATUS_PUSH_INTERVAL = 30        # Push every ~30 frames (~once per second)

    print("[MegaDashboard] Starting main loop. Press 'q' to quit.")
    print(f"[MegaDashboard] Anomaly score panel: {args.show_anomaly_panel} (docked: {args.panel_side})")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            loop_start = time.time()

            # --- 1. Pose model (Main track, runs every frame) ---
            pose_results = pose_model.track(frame, persist=True, verbose=False)[0]
            annotated = pose_results.plot()

            visible_tracks = track_manager.update(pose_results)
            track_alert_types = {tid: set() for tid in visible_tracks}
            fight_confidence_map = {}  # Store confidence scores for debugging

            for tid, track in visible_tracks.items():
                if not track.ready():
                    continue

                # Detect fall (now with state machine: IDLE→CANDIDATE→CONFIRMED→RECOVERY)
                if track.detect_fall():
                    track_alert_types[tid].add("fall")

                # Detect running (now with state machine)
                if track.detect_running():
                    track_alert_types[tid].add("running")

            # Pairwise fight detection (now returns 4-tuple: status, overlap, confidence, event)
            for (id_a, track_a), (id_b, track_b) in itertools.combinations(visible_tracks.items(), 2):
                status, overlap, confidence, event = check_fight(track_a, track_b)
                if status == "fight_detected":
                    track_alert_types[id_a].add("fight")
                    track_alert_types[id_b].add("fight")
                    # Store confidence for optional debug visualization
                    fight_confidence_map[(id_a, id_b)] = (overlap, confidence)

            # High-priority events trigger increased fire/smoke detection
            priority_active = any(types & {"fall", "fight"} for types in track_alert_types.values())
            priority_controller.update(priority_active)

            # --- 2. Object & Crowd model (Time-sliced, runs every Nth frame) ---
            if frame_idx % args.frame_skip == 0:
                obj_results = object_model.predict(frame, verbose=False)[0]

                new_banned_counts = {}
                new_banned_boxes = []
                new_people_boxes = []

                for box in obj_results.boxes:
                    cls_id = int(box.cls)
                    name = obj_results.names[cls_id]
                    xyxy = box.xyxy[0].tolist()

                    if cls_id == 0:  # Person
                        new_people_boxes.append(xyxy)
                    elif cls_id in BANNED_CLASS_IDS:  # Anomaly Object
                        new_banned_counts[name] = new_banned_counts.get(name, 0) + 1
                        new_banned_boxes.append((xyxy, name))

                # Update caches
                cached_banned_counts = new_banned_counts
                cached_banned_boxes = new_banned_boxes
                cached_people_boxes = new_people_boxes
                cached_crowd_status = CrowdStatus(
                    count=len(new_people_boxes),
                    raw_count=len(new_people_boxes),
                    is_crowd=(len(new_people_boxes) >= args.crowd_density_threshold),
                    method="yolo_object"
                )

            frame_idx += 1

            # Draw cached non-pose objects onto the frame
            for (xyxy, name) in cached_banned_boxes:
                x1, y1, x2, y2 = [int(v) for v in xyxy]
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 165, 255), 2)  # Orange for banned objects
                cv2.putText(annotated, name, (x1, max(0, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

            # Draw tiny green boxes for crowd (just heads/bodies)
            for xyxy in cached_people_boxes:
                x1, y1, x2, y2 = [int(v) for v in xyxy]
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 1)

            # --- 3. Fire/smoke (Background thread) ---
            fs_status = FireSmokeStatus()
            if fire_smoke_detector is not None:
                fire_smoke_detector.update_frame(frame)
                fs_status = fire_smoke_detector.get_status()

            # --- HUD overlay ---
            annotated = draw_hud_overlay(
                annotated, fs_status, cached_crowd_status,
                crowd_density_threshold=args.crowd_density_threshold,
            )

            # --- 4. Alert Triggers ---
            person_events = [(visible_tracks[tid].bboxes[-1], types) for tid, types in track_alert_types.items() if types]
            wide_types = set()
            if fs_status.fire:
                wide_types.add("fire")
            if fs_status.smoke:
                wide_types.add("smoke")
            if cached_crowd_status.is_crowd:
                wide_types.add("crowd")
            if cached_banned_counts:
                wide_types.add("object_anomaly")

            alert_manager.update(person_events, wide_types, cached_banned_counts)
            annotated = alert_manager.draw(annotated)
            if alert_manager.is_active:
                alert_manager.maybe_log(annotated)

            # --- Push live detection status to the Flask backend (throttled) ---
            # This is the "last missing link" — it ensures the front-end
            # /detections/latest endpoint returns real-time YOLO results
            # instead of trying to open its own camera (which would 503
            # when the webcam is already held by this process).
            _status_push_counter += 1
            if dashboard_client is not None and _status_push_counter >= _STATUS_PUSH_INTERVAL:
                _status_push_counter = 0
                # Collect detections from every analysis layer into a
                # unified list compatible with the front-end overlay.
                status_detections = []
                # Fire/smoke from background thread
                if fs_status.fire:
                    status_detections.append({
                        "class": "Fire",
                        "confidence": round(fs_status.fire_confidence, 2),
                        "bbox": [0, 0, 100, 100],
                    })
                if fs_status.smoke:
                    status_detections.append({
                        "class": "Smoke",
                        "confidence": round(fs_status.smoke_confidence, 2),
                        "bbox": [0, 0, 100, 100],
                    })
                # Crowd detection
                if cached_crowd_status.is_crowd or cached_crowd_status.count > 0:
                    status_detections.append({
                        "class": "Crowd",
                        "confidence": round(min(1.0, cached_crowd_status.count / max(1, args.crowd_density_threshold)), 2),
                        "bbox": [0, 0, 100, 100],
                    })
                dashboard_client.send_detection_status(
                    fire=fs_status.fire,
                    smoke=fs_status.smoke,
                    crowd=cached_crowd_status.is_crowd,
                    detections=status_detections,
                    camera_id=args.camera_id,
                    area_m2=cached_crowd_status.area_m2,
                    density_people_per_m2=cached_crowd_status.density_people_per_m2,
                    zone_densities=cached_crowd_status.zone_densities,
                    head_positions_world=cached_crowd_status.head_positions_world,
                )

            # --- Anomaly Score Panel & FPS readout ---
            frame_times.append(time.time() - loop_start)
            if len(frame_times) > 30:
                frame_times.pop(0)
            fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else 0.0

            # Draw the single clean anomaly score panel (FPS + all six scores)
            if args.show_anomaly_panel:
                ready_tracks = [t for t in visible_tracks.values() if t.ready()]

                fall_confirmed = sum(1 for t in ready_tracks if t.fall_state == "CONFIRMED")
                fall_candidate = sum(1 for t in ready_tracks if t.fall_state == "CANDIDATE")
                fall_score = 1.0 if fall_confirmed else (0.5 if fall_candidate else 0.0)
                fall_value = f"{fall_confirmed} confirmed" if fall_confirmed else (
                    f"{fall_candidate} candidate" if fall_candidate else "clear")

                run_confirmed = sum(1 for t in ready_tracks if t.run_state == "CONFIRMED")
                run_candidate = sum(1 for t in ready_tracks if t.run_state == "CANDIDATE")
                run_score = 1.0 if run_confirmed else (0.5 if run_candidate else 0.0)
                run_value = f"{run_confirmed} confirmed" if run_confirmed else (
                    f"{run_candidate} candidate" if run_candidate else "clear")

                fight_pairs = len(fight_confidence_map)
                fight_score = min(1.0, max((c for _, c in fight_confidence_map.values()), default=0.0)) \
                    if fight_pairs else 0.0
                fight_value = f"{fight_pairs} pair(s)" if fight_pairs else "clear"

                fire_score = 1.0 if fs_status.fire else 0.0
                fire_value = "DETECTED" if fs_status.fire else "clear"

                smoke_score = 1.0 if fs_status.smoke else 0.0
                smoke_value = "DETECTED" if fs_status.smoke else "clear"

                crowd_score = min(1.0, cached_crowd_status.count / max(1, args.crowd_density_threshold))
                object_total = sum(cached_banned_counts.values())
                crowd_value = f"{cached_crowd_status.count} ppl"
                if object_total:
                    crowd_score = max(crowd_score, 1.0)
                    crowd_value += f", {object_total} obj"

                scores = [
                    ("FALL", fall_score, fall_value),
                    ("RUNNING", run_score, run_value),
                    ("FIGHT", fight_score, fight_value),
                    ("FIRE", fire_score, fire_value),
                    ("SMOKE", smoke_score, smoke_value),
                    ("CROWD", crowd_score, crowd_value),
                ]

                annotated = draw_anomaly_score_panel(annotated, scores, fps, side=args.panel_side)

            # Publish the fully-annotated frame for the MJPEG stream.
            # Push AFTER the SENTINEL anomaly score panel is drawn so dashboard
            # viewers see the same complete frame as the OpenCV window.
            if frame_broadcaster is not None:
                frame_broadcaster.update(annotated)

            if annotated.shape[1] != args.display_width:
                scale = args.display_width / annotated.shape[1]
                annotated = cv2.resize(annotated, (args.display_width, int(annotated.shape[0] * scale)))

            cv2.imshow("Sentinel - Mega Dashboard (v5.3.1)", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if fire_smoke_detector is not None:
            fire_smoke_detector.stop()
        if dashboard_client is not None:
            dashboard_client.stop()
        print("[MegaDashboard] Shut down cleanly.")


if __name__ == "__main__":
    main()
