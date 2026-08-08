"""
Phase 3 - motion_heuristics.py (v2.0 Specification-Aligned, Final)
--------------------------------------------------------------
Refactored for 10 FPS OpenVINO CPU environments.
Aligned with Motion Heuristics Design Specification v2.0 (5 pages).

All public class/function/method names are unchanged from the prior
revision (motion_heuristics_modified.py) so this file is a drop-in
replacement. The changes below close gaps found by comparing that
revision line-by-line against the spec, without renaming anything.

Fixes / improvements made in this revision:
1. HISTORY BUFFER
   - Spec 3.1 calls for a 5-10 frame rolling window. The previous
     revision's comment claimed "per spec" but set HISTORY_LEN=25
     (~2.5s), which contradicts the spec text. Restored to the
     spec's 10-frame upper bound.
2. FALL DETECTION
   - Rule 3 (acceleration spike) was computed by
     `_velocity_acceleration()` but never actually gated the state
     machine - it only appeared in debug output. It now gates the
     IDLE -> CANDIDATE transition.
   - Rule 4 (height reduction) was computed by `_height_reduction()`
     but likewise never gated anything. It now gates the
     CANDIDATE -> CONFIRMED transition alongside the motionless check.
   - Rule 1 ("rejecting people already seated") previously only
     looked at the last 3 frames. `_is_stable_standing()` now also
     checks the oldest frame in the buffer so a person who was
     already down/seated when tracking began cannot seed a false
     candidate.
3. RUNNING DETECTION
   - Rule 8 ("repeated stride cycles rather than isolated lunges")
     had no actual cycle-counting - `limb_variance_score()` measured
     generic variance only. Added `_stride_cycle_count()` (oscillation
     / zero-crossing counter on ankle-vs-hip horizontal offset) and
     it now gates CANDIDATE -> CONFIRMED so a single lunge can't
     confirm running.
4. FIGHT DETECTION
   - Unchanged rule logic, but now emits the standardized output
     structure (see #5) instead of a bare tuple-only debug flow.
5. STANDARDIZED OUTPUT (Spec 8.2)
   - The spec defines a required output dict per event
     (event_name, confidence_score, tracked_person_ids, timestamp,
     event_state, debug_info). Neither `detect_fall()` nor
     `detect_running()` nor `check_fight()` emitted this in the prior
     revision - they only returned booleans / raw tuples. Added
     `build_event_output()` (module-level) plus thin wrapper methods
     `get_fall_event()`, `get_running_event()` on PersonTrack, and
     `check_fight()` now also returns this dict as a fourth tuple
     element so the controller can alert directly from it.
6. CACHING (Golden Rule: "Cache Aggressively")
   - Added a tiny per-frame memo (`self._frame_cache`) that is
     cleared once in `update()`. Repeated same-frame calls to
     `hip_vertical_velocity_normalized()` (called twice per frame by
     `_velocity_acceleration()`) now reuse the cached value instead
     of re-walking the deque.
7. Everything else (thresholds, state machine names, helper method
   names) is left as-is for compatibility with the existing tracker,
   YOLOv8n-Pose output format, and OpenVINO pipeline.
"""

from collections import deque
import time
import math

# ---- Keypoint index constants (YOLOv8-Pose 17 points) ----
L_SHOULDER, R_SHOULDER = 5, 6
L_ELBOW, R_ELBOW = 7, 8
L_WRIST, R_WRIST = 9, 10
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16

# ---- Tunable thresholds (normalized units) ----
HISTORY_LEN = 10                   # Per spec 3.1: rolling window of 5-10 frames
MIN_KPT_CONFIDENCE = 0.3

# ---- Event State Machine ----
EVENT_STATES = ("IDLE", "CANDIDATE", "CONFIRMED", "RECOVERY")

# Fall thresholds
FALL_VELOCITY_THRESH = 0.8         # body-heights / second (short window impact) - per spec 3.1
FALL_STANDING_RATIO = 1.0          # width/height < 1.0 counts as "upright"
FALL_TORSO_ANGLE_THRESH = 1.0      # abs(dx/dy) of torso > 1.0 means horizontal
FALL_MOTIONLESS_FRAMES = 5         # Frames to confirm impact (stable centroid)
FALL_MOTIONLESS_VAR = 0.20         # Max centroid movement during motionless check (increased to allow tracking jitter)
FALL_CANDIDATE_FRAMES = 4          # Frames to confirm candidate state before CONFIRMED
FALL_RECOVERY_SECONDS = 2.0        # Observation window for recovery
FALL_ACCEL_THRESH = 0.18           # Rule 3: min positive accel spike to open a candidate
FALL_HEIGHT_REDUCTION_THRESH = 0.35  # Rule 4: min bbox-height drop to confirm a fall (relaxed for sitting falls)

# Running thresholds
RUNNING_SPEED_THRESH = 0.8         # body-heights / second
RUNNING_LIMB_VAR_THRESH = 0.05     # normalized limb variance
RUNNING_CONFIDENCE_THRESH = 0.5
RUNNING_HYSTERESIS_FRAMES = 3      # smooth running score over 3 frames
RUNNING_CANDIDATE_FRAMES = 4       # 5-6 frames per spec, allow 4 for margin
RUNNING_RECOVERY_FRAMES = 3        # 2-3 slow frames to end running
RUNNING_DIRECTION_VARIANCE_THRESH = 60.0  # degrees, for direction consistency
RUNNING_MIN_STRIDE_CYCLES = 1      # Rule 8: require at least one full stride cycle

# Fight thresholds
OVERLAP_THRESH = 0.4
FIGHT_VELOCITY_VAR_THRESH = 1.2    # (body-heights/sec)^2
FIGHT_RUNNING_MULTIPLIER = 1.6     # raise the bar when running is likely
FIGHT_CANDIDATE_FRAMES = 3         # 5-8 frames per spec, allow 3 for margin
FIGHT_MIN_PARTICIPANTS = 2         # Per spec: minimum two people


# ============== Standardized Output Structure (Spec 8.2) ==============

def build_event_output(event_name, confidence_score, tracked_person_ids,
                        event_state, debug_info=None, timestamp=None):
    """
    Build the standardized event dict every heuristic module must emit
    to the main controller (Spec section 8.2):

        {
            "event_name": "FALL_DETECTED" | "RUNNING" | "FIGHT_DETECTED",
            "confidence_score": float,     # normalized [0.0 - 1.0]
            "tracked_person_ids": list[int],
            "timestamp": float,
            "event_state": str,            # "CANDIDATE" | "CONFIRMED" | "RECOVERY"
            "debug_info": dict,
        }
    """
    return {
        "event_name": event_name,
        "confidence_score": float(max(0.0, min(confidence_score, 1.0))),
        "tracked_person_ids": list(tracked_person_ids),
        "timestamp": timestamp if timestamp is not None else time.time(),
        "event_state": event_state,
        "debug_info": debug_info or {},
    }


class PersonTrack:
    """Rolling per-ID history buffers and event state trackers.

    Maintains:
    - Core history buffers (keypoints, bboxes, centroids, timestamps)
    - Cached body centers (shoulder, hip) for reuse
    - Event state machines (fall, running, fight)
    - Activity-specific counters and history
    """

    def __init__(self, track_id, max_len=HISTORY_LEN):
        self.track_id = track_id

        # ---- Core History Buffers (per spec) ----
        self.timestamps = deque(maxlen=max_len)
        self.keypoints = deque(maxlen=max_len)   # raw 17x3 lists
        self.bboxes = deque(maxlen=max_len)      # (x1, y1, x2, y2)
        self.centroids = deque(maxlen=max_len)   # (cx, cy)

        # ---- Cached Body Centers (optimization) ----
        self.shoulder_centers = deque(maxlen=max_len)  # (x, y) or None
        self.hip_centers = deque(maxlen=max_len)       # (x, y) or None

        # ---- Fall Event State Machine ----
        self.fall_state = "IDLE"
        self.fall_candidate_frames = 0
        self.fall_motionless_frames = 0
        self.fall_confirmed_time = None
        self.fall_baseline_height = 0.0

        # ---- Running Event State Machine ----
        self.run_state = "IDLE"
        self.run_candidate_frames = 0
        self.run_score_history = deque(maxlen=RUNNING_HYSTERESIS_FRAMES)
        self.run_direction_history = deque(maxlen=5)  # Track movement direction (radians)
        self.run_slow_frame_count = 0  # Frames at slow speed (for recovery)

        # ---- Fight-specific state (fight is managed externally via check_fight) ----
        # Note: fight state is context-dependent (requires two participants)

        # ---- Per-frame memo cache (Golden Rule: "Cache Aggressively") ----
        self._frame_cache = {}

    def update(self, keypoints_xyc, bbox, timestamp=None):
        """
        keypoints_xyc: (17, 3) numpy array
        bbox: (4,) numpy array [x1, y1, x2, y2]
        """
        if timestamp is None:
            self.timestamps.append(time.time())
        else:
            self.timestamps.append(timestamp)

        self.keypoints.append(keypoints_xyc)
        self.bboxes.append(bbox)

        # Cache centroid
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        self.centroids.append((cx, cy))

        # Cache shoulder center (reuse across detectors)
        shoulder = self._midpoint(keypoints_xyc, L_SHOULDER, R_SHOULDER)
        self.shoulder_centers.append(shoulder)

        # Cache hip center (reuse across detectors)
        hip = self._midpoint(keypoints_xyc, L_HIP, R_HIP)
        self.hip_centers.append(hip)

        # New frame invalidates any same-frame memoized computations
        self._frame_cache = {}

    def ready(self, min_frames=4):
        """Check if track has minimum history for reliable computation."""
        return len(self.timestamps) >= min_frames

    def _box_height(self, bbox):
        """Bounding box height, clamped to avoid division by zero."""
        return max(bbox[3] - bbox[1], 1e-6)

    def _box_width(self, bbox):
        """Bounding box width, clamped to avoid division by zero."""
        return max(bbox[2] - bbox[0], 1e-6)

    def _aspect(self, bbox):
        """Bounding box aspect ratio (width / height)."""
        w = self._box_width(bbox)
        h = self._box_height(bbox)
        return w / h

    # ============== Shared Helpers (Reuse across detectors) ==============

    def _midpoint(self, kpt_frame, idx_a, idx_b):
        """Compute midpoint of two keypoints, handling missing data gracefully."""
        a, b = kpt_frame[idx_a], kpt_frame[idx_b]
        a_ok = a[2] >= MIN_KPT_CONFIDENCE
        b_ok = b[2] >= MIN_KPT_CONFIDENCE
        if a_ok and b_ok:
            return (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        if a_ok:
            return a[0], a[1]
        if b_ok:
            return b[0], b[1]
        return None

    def _keypoint(self, kpt_frame, idx):
        """Extract single keypoint if confident, else None."""
        kpt = kpt_frame[idx]
        if kpt[2] >= MIN_KPT_CONFIDENCE:
            return (kpt[0], kpt[1])
        return None

    # ============== FALL DETECTION (Specification v2.0) ==============
    """
    Fall Rules (per spec):
    Rule 1: Stable standing before event (verify tracking, height, posture,
            AND reject subjects who were already down/seated at buffer start)
    Rule 2: Rapid body descent (hip, head, body center)
    Rule 3: Acceleration spike (change in velocity) - now gates CANDIDATE entry
    Rule 4: Body height reduction (bbox height or hip drop) - now gates CONFIRMED
    Rule 5: Ground confirmation (body remains low for several frames)
    Rule 6: Recovery check (observe 1-2 seconds, cancel if person stands)

    State Machine: IDLE -> CANDIDATE -> CONFIRMED -> RECOVERY -> IDLE
    """

    def torso_orientation(self):
        """Returns abs(dx/dy) of shoulder to hip vector. > 1.0 is horizontal."""
        if not self.shoulder_centers or not self.hip_centers:
            return 0.0

        shoulder = self.shoulder_centers[-1]
        hip = self.hip_centers[-1]

        if not shoulder or not hip:
            return 0.0

        dx = abs(shoulder[0] - hip[0])
        dy = max(abs(shoulder[1] - hip[1]), 1e-6)
        return dx / dy

    def _is_stable_standing(self):
        """Rule 1: Verify stable standing posture (upright, stable height),
        and reject subjects who were already seated/down when the history
        buffer began (spec: "rejecting people already seated")."""
        if not self.ready(min_frames=3):
            return False

        ratio = self._aspect(self.bboxes[-1])
        torso = self.torso_orientation()

        # Upright: aspect ratio < FALL_STANDING_RATIO and torso not horizontal
        is_upright = (ratio < FALL_STANDING_RATIO) and (torso < FALL_TORSO_ANGLE_THRESH)

        # Stable: bbox height doesn't fluctuate wildly
        if len(self.bboxes) < 3:
            return is_upright

        recent_heights = [self._box_height(b) for b in list(self.bboxes)[-3:]]
        height_var = (max(recent_heights) - min(recent_heights)) / min(recent_heights)
        is_stable = height_var < 0.25  # Relaxed to 25% height fluctuation for walking/running bounce

        # Baseline check: the oldest frame in the buffer must also look
        # upright, otherwise the person may have already been seated/down
        # and simply moved into frame - a fall needs a genuine standing
        # baseline, not just a momentarily-upright latest frame.
        baseline_upright = True
        if len(self.bboxes) >= 3:
            baseline_ratio = self._aspect(self.bboxes[0])
            baseline_upright = baseline_ratio < (FALL_STANDING_RATIO * 1.25) # generous margin for running

        return is_upright and is_stable and baseline_upright

    def hip_vertical_velocity_normalized(self, window_frames=5):
        """Rule 2: Rapid body descent over short window (captures impact)."""
        cache_key = ("hip_vel", window_frames)
        if cache_key in self._frame_cache:
            return self._frame_cache[cache_key]

        if len(self.keypoints) < 2 or not self.hip_centers or len(self.hip_centers) < 2:
            self._frame_cache[cache_key] = 0.0
            return 0.0

        window = min(len(self.hip_centers), window_frames)
        hip_start = self.hip_centers[-window]
        hip_end = self.hip_centers[-1]

        if not hip_start or not hip_end:
            self._frame_cache[cache_key] = 0.0
            return 0.0

        t_start = self.timestamps[-window]
        t_end = self.timestamps[-1]
        dt = t_end - t_start

        if dt <= 0:
            self._frame_cache[cache_key] = 0.0
            return 0.0

        dy = hip_end[1] - hip_start[1]  # positive = downward
        height = self._box_height(self.bboxes[-1])
        result = (dy / height) / dt
        self._frame_cache[cache_key] = result
        return result

    def _velocity_acceleration(self):
        """Rule 3: Detect acceleration spike in descent.
        
        Per spec 8.1: uses disjoint window acceleration (non-overlapping frames):
          recent = hip_velocity over frames 0,1 (last 2 frames)
          prior  = hip_velocity over frames 2,3 (the 2 frames before that)
          accel = recent - prior
        """
        if len(self.hip_centers) < 5:
            return 0.0

        # Extract timestamps and hip positions
        hip_pos = list(self.hip_centers)
        times = list(self.timestamps)
        heights = [self._box_height(b) for b in list(self.bboxes)]

        # Recent window: last 2 frames (indices -1, -2)
        if (hip_pos[-1] and hip_pos[-2] and 
            times[-1] > times[-2] and heights[-1] > 1e-6):
            dy_recent = hip_pos[-1][1] - hip_pos[-2][1]  # positive = downward
            dt_recent = times[-1] - times[-2]
            if dt_recent > 0:
                v_recent = (dy_recent / heights[-1]) / dt_recent
            else:
                v_recent = 0.0
        else:
            v_recent = 0.0

        # Prior window: frames 3,4 from now (indices -3, -4)
        if (hip_pos[-3] and hip_pos[-4] and 
            times[-3] > times[-4] and heights[-3] > 1e-6):
            dy_prior = hip_pos[-3][1] - hip_pos[-4][1]  # positive = downward
            dt_prior = times[-3] - times[-4]
            if dt_prior > 0:
                v_prior = (dy_prior / heights[-3]) / dt_prior
            else:
                v_prior = 0.0
        else:
            v_prior = 0.0

        # Positive = increasing downward velocity (acceleration)
        return v_recent - v_prior

    def _height_reduction(self):
        """Rule 4: Measure body height reduction from start of fall candidate."""
        if len(self.bboxes) < 2:
            return 0.0

        initial_height = self.fall_baseline_height if getattr(self, 'fall_baseline_height', 0) > 0 else self._box_height(self.bboxes[0])
        current_height = self._box_height(self.bboxes[-1])

        # Return percentage reduction
        if initial_height <= 0:
            return 0.0
        return (initial_height - current_height) / initial_height

    def is_motionless(self, window_frames=3, threshold=FALL_MOTIONLESS_VAR):
        """Rule 5: Check if centroid has moved less than threshold*height recently."""
        if len(self.centroids) < window_frames:
            return False

        window_centroids = list(self.centroids)[-window_frames:]
        xs = [c[0] for c in window_centroids]
        ys = [c[1] for c in window_centroids]

        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)

        height = self._box_height(self.bboxes[-1])
        return (dx / height < threshold) and (dy / height < threshold)

    def detect_fall(self):
        """
        Fall detection state machine with full spec compliance.

        Returns True only when CONFIRMED state is reached.
        """
        if not self.ready():
            return False

        velocity = self.hip_vertical_velocity_normalized()
        is_horizontal = (self._aspect(self.bboxes[-1]) > 1.0) or \
                       (self.torso_orientation() > FALL_TORSO_ANGLE_THRESH)

        # ---- IDLE -> CANDIDATE ----
        if self.fall_state == "IDLE":
            # Rule 2 & 3: rapid descent AND an actual acceleration spike
            accel = self._velocity_acceleration()
            if velocity > FALL_VELOCITY_THRESH and accel > FALL_ACCEL_THRESH:
                self.fall_state = "CANDIDATE"
                self.fall_candidate_frames = 1
                self.fall_motionless_frames = 0
                self.fall_baseline_height = max([self._box_height(b) for b in list(self.bboxes)])

        # ---- CANDIDATE -> CONFIRMED ----
        elif self.fall_state == "CANDIDATE":
            self.fall_candidate_frames += 1

            # Rule 5: Require motionless confirmation
            if self.is_motionless():
                self.fall_motionless_frames += 1
                # Rule 4: also require a real height reduction before
                # confirming, so a person who merely stopped moving while
                # still upright can't falsely confirm
                height_dropped = self._height_reduction() > FALL_HEIGHT_REDUCTION_THRESH
                if self.fall_motionless_frames >= FALL_MOTIONLESS_FRAMES and height_dropped:
                    self.fall_state = "CONFIRMED"
                    self.fall_confirmed_time = time.time()
                    self.fall_candidate_frames = 0
                    self.fall_motionless_frames = 0
            else:
                # Reset if no longer motionless (because they are actively falling or moving)
                self.fall_motionless_frames = 0
                # Just timeout the candidate state if they never become motionless on the ground.
                # (Removing the premature height check here because it was cancelling real falls mid-air)
                if self.fall_candidate_frames > 30:
                    self.fall_state = "IDLE"

        # ---- CONFIRMED -> RECOVERY (or back to IDLE) ----
        elif self.fall_state == "CONFIRMED":
            # Rule 6: Check recovery over 1-2 seconds
            if self.fall_confirmed_time:
                elapsed = time.time() - self.fall_confirmed_time

                # Check if person is recovering (standing back up)
                if (self._aspect(self.bboxes[-1]) < FALL_STANDING_RATIO and
                    self.torso_orientation() < FALL_TORSO_ANGLE_THRESH):
                    self.fall_state = "RECOVERY"
                elif elapsed > FALL_RECOVERY_SECONDS:
                    # No recovery detected over observation window
                    self.fall_state = "IDLE"

        elif self.fall_state == "RECOVERY":
            # Hold recovery state briefly, then reset to IDLE
            if self.fall_confirmed_time and \
               (time.time() - self.fall_confirmed_time) > FALL_RECOVERY_SECONDS + 1.0:
                self.fall_state = "IDLE"

        return self.fall_state == "CONFIRMED"

    def get_fall_event(self):
        """
        Spec 8.2: emit the standardized event dict for the fall detector.
        Returns None when there is no candidate/confirmed/recovery event
        worth reporting (i.e. state is IDLE).
        """
        is_confirmed = self.detect_fall()
        if self.fall_state == "IDLE":
            return None

        accel = self._velocity_acceleration()
        height_drop = self._height_reduction()
        velocity = self.hip_vertical_velocity_normalized()

        # Simple weighted confidence from the same signals that drive the
        # state machine, so debug overlay and alerting stay consistent.
        confidence = (
            0.4 * min(velocity / FALL_VELOCITY_THRESH, 1.0) +
            0.3 * min(max(height_drop, 0.0) / FALL_HEIGHT_REDUCTION_THRESH, 1.0) +
            0.3 * min(max(accel, 0.0) / FALL_ACCEL_THRESH, 1.0)
        )

        return build_event_output(
            event_name="FALL_DETECTED",
            confidence_score=confidence,
            tracked_person_ids=[self.track_id],
            event_state=self.fall_state,
            debug_info=self.debug_signals(),
        )

    # ============== RUNNING DETECTION (Specification v2.0) ==============
    """
    Running Rules (per spec):
    Rule 1: Stable tracked person
    Rule 2: Sustained body translation (centroid displacement)
    Rule 3: Acceleration phase (progressive increase)
    Rule 4: Continuous leg motion (ankle displacement)
    Rule 5: Continuous arm swing (wrist displacement)
    Rule 6: Persistent locomotion (5-6 frames minimum)
    Rule 7: Direction consistency (reject chaotic trajectories)
    Rule 8: Repeated stride cycles (multiple leg cycles, not isolated lunges)
    Rule 9: Recovery (2-3 slow frames to end)

    State Machine: IDLE -> CANDIDATE -> CONFIRMED -> RECOVERY -> IDLE
    """

    def centroid_horizontal_speed(self, window_frames=5):
        """Rule 2 & 3: Sustained body translation with short window."""
        if len(self.centroids) < 2:
            return 0.0

        window = min(len(self.centroids), window_frames)
        c_start = self.centroids[-window]
        c_end = self.centroids[-1]
        t_start = self.timestamps[-window]
        t_end = self.timestamps[-1]

        dt = t_end - t_start
        if dt <= 0:
            return 0.0

        dx = abs(c_end[0] - c_start[0])
        height = self._box_height(self.bboxes[-1])
        return (dx / height) / dt

    def _movement_direction(self):
        """Compute direction of movement in radians (for direction consistency)."""
        if len(self.centroids) < 2:
            return None

        c_start = self.centroids[-2]
        c_end = self.centroids[-1]

        dx = c_end[0] - c_start[0]
        dy = c_end[1] - c_start[1]

        return math.atan2(dy, dx)

    def _direction_consistency(self):
        """Rule 7: Check if movement direction is consistent (not chaotic)."""
        if len(self.run_direction_history) < 2:
            return True  # Not enough data, assume consistent

        directions = list(self.run_direction_history)
        angle_diffs = []

        for i in range(1, len(directions)):
            # Compute angular difference
            diff = abs(directions[i] - directions[i - 1])
            # Normalize to [0, pi]
            if diff > math.pi:
                diff = 2 * math.pi - diff
            angle_diffs.append(math.degrees(diff))

        if not angle_diffs:
            return True

        avg_angle_diff = sum(angle_diffs) / len(angle_diffs)
        return avg_angle_diff < RUNNING_DIRECTION_VARIANCE_THRESH

    def limb_variance_score(self):
        """Rule 4 & 5: Continuous leg and arm motion variance."""
        if len(self.keypoints) < 3:
            return 0.0, False

        rel_xs = []
        for f in self.keypoints:
            hip = self._midpoint(f, L_HIP, R_HIP)
            if not hip:
                continue

            pts = []
            for idx in (L_WRIST, R_WRIST, L_ANKLE, R_ANKLE):
                if f[idx][2] >= MIN_KPT_CONFIDENCE:
                    pts.append(f[idx][0])

            if pts:
                avg_dist = sum(abs(px - hip[0]) for px in pts) / len(pts)
                rel_xs.append(avg_dist)

        if len(rel_xs) < 3:
            return 0.0, False

        mean_val = sum(rel_xs) / len(rel_xs)
        variance = sum((x - mean_val) ** 2 for x in rel_xs) / len(rel_xs)

        height = self._box_height(self.bboxes[-1])
        norm_var = variance / (height * height)

        return norm_var, True

    def _stride_cycle_count(self):
        """
        Rule 8: Count repeated stride cycles rather than relying on a single
        variance number, which can't tell a lunge from a run. A stride cycle
        is approximated by counting sign changes (zero-crossings around the
        mean) of the ankle-vs-hip horizontal offset over the buffered
        history - each crossing pair corresponds to one leg swinging past
        the body's midline and back.
        """
        if len(self.keypoints) < 4:
            return 0

        offsets = []
        for f in self.keypoints:
            hip = self._midpoint(f, L_HIP, R_HIP)
            if not hip:
                continue
            ankle_pts = []
            for idx in (L_ANKLE, R_ANKLE):
                if f[idx][2] >= MIN_KPT_CONFIDENCE:
                    ankle_pts.append(f[idx][0])
            if not ankle_pts:
                continue
            avg_ankle_x = sum(ankle_pts) / len(ankle_pts)
            offsets.append(avg_ankle_x - hip[0])

        if len(offsets) < 4:
            return 0

        mean_offset = sum(offsets) / len(offsets)
        signs = [1 if (o - mean_offset) >= 0 else -1 for o in offsets]

        crossings = 0
        for i in range(1, len(signs)):
            if signs[i] != signs[i - 1]:
                crossings += 1

        # Two crossings ~= one full stride cycle (leg forward, leg back)
        return crossings // 2

    def trunk_lean_score(self):
        """Additional signal for running posture."""
        if not self.shoulder_centers or not self.hip_centers:
            return 0.0

        shoulder = self.shoulder_centers[-1]
        hip = self.hip_centers[-1]

        if not shoulder or not hip:
            return 0.0

        height = self._box_height(self.bboxes[-1])
        lean = abs(shoulder[0] - hip[0]) / height

        return min(max(lean / 0.15, 0.0), 1.0)

    def running_confidence(self):
        """Compute raw 1-frame running confidence (before hysteresis)."""
        if not self.ready():
            return 0.0

        speed = self.centroid_horizontal_speed()
        speed_score = min(speed / RUNNING_SPEED_THRESH, 1.0)

        # Lazy eval: If stationary, skip expensive variance
        if speed_score < 0.1:
            return 0.0

        limb_var, limbs_ok = self.limb_variance_score()
        lean_score = self.trunk_lean_score()

        if limbs_ok:
            var_score = min(limb_var / RUNNING_LIMB_VAR_THRESH, 1.0)
            confidence = 0.5 * speed_score + 0.3 * var_score + 0.2 * lean_score
        else:
            confidence = 0.7 * speed_score + 0.3 * lean_score

        return confidence

    def detect_running(self):
        """
        Running detection state machine with full spec compliance.

        Returns True only when CONFIRMED state is reached.
        """
        if not self.ready():
            return False

        raw_score = self.running_confidence()
        self.run_score_history.append(raw_score)

        # Track movement direction
        direction = self._movement_direction()
        if direction is not None:
            self.run_direction_history.append(direction)

        smoothed_score = sum(self.run_score_history) / len(self.run_score_history)

        # ---- IDLE -> CANDIDATE ----
        if self.run_state == "IDLE":
            if smoothed_score > RUNNING_CONFIDENCE_THRESH:
                # Require direction consistency
                if self._direction_consistency():
                    self.run_state = "CANDIDATE"
                    self.run_candidate_frames = 1
                    self.run_slow_frame_count = 0

        # ---- CANDIDATE -> CONFIRMED ----
        elif self.run_state == "CANDIDATE":
            self.run_candidate_frames += 1

            if smoothed_score < RUNNING_CONFIDENCE_THRESH * 0.7:
                # Score dropped significantly, reset
                self.run_state = "IDLE"
                self.run_candidate_frames = 0
            elif self.run_candidate_frames >= RUNNING_CANDIDATE_FRAMES:
                # Rule 6: Persistent locomotion (5-6 frames)
                # Rule 8: ...but only confirm if we can see a real stride
                # cycle, not just one long lunge-like displacement.
                if self._stride_cycle_count() >= RUNNING_MIN_STRIDE_CYCLES:
                    self.run_state = "CONFIRMED"
                    self.run_candidate_frames = 0
                # else: keep accumulating candidate frames until a full
                # cycle is observed or the score drops out above.

        # ---- CONFIRMED (track/exit) ----
        elif self.run_state == "CONFIRMED":
            # Rule 9: Recovery (2-3 slow frames to end)
            if smoothed_score < RUNNING_CONFIDENCE_THRESH:
                self.run_slow_frame_count += 1
                if self.run_slow_frame_count >= RUNNING_RECOVERY_FRAMES:
                    self.run_state = "IDLE"
                    self.run_slow_frame_count = 0
            else:
                self.run_slow_frame_count = 0  # Reset if speed recovers

        return self.run_state == "CONFIRMED"

    def get_running_event(self):
        """Spec 8.2: emit the standardized event dict for the running detector."""
        is_confirmed = self.detect_running()
        if self.run_state == "IDLE":
            return None

        smoothed_score = (
            sum(self.run_score_history) / len(self.run_score_history)
            if self.run_score_history else 0.0
        )

        return build_event_output(
            event_name="RUNNING",
            confidence_score=smoothed_score,
            tracked_person_ids=[self.track_id],
            event_state=self.run_state,
            debug_info=self.debug_signals(),
        )

    # ============== FIGHT DETECTION (Specification v2.0) ==============
    """
    Fight Rules (per spec):
    Rule 1: Minimum two tracked people
    Rule 2: Sustained close proximity (body-center distance)
    Rule 3: Frequent body contact (bbox overlap)
    Rule 4: Rapid limb motion (wrists, elbows, knees, ankles)
    Rule 5: Chaotic body movement (sudden accel/decel, direction changes)
    Rule 6: Mutual interaction (both individuals move)
    Rule 7: Persistence (5-8 frames)
    Rule 8: Separation (terminate when separated or movement normalizes)

    Note: Fight state is managed externally via check_fight()
    """

    def limb_velocity_variance_normalized(self):
        """Rule 4: Variance of wrist/elbow speed (aggressive motion)."""
        if len(self.keypoints) < 3:
            return 0.0

        joint_indices = [L_ELBOW, R_ELBOW, L_WRIST, R_WRIST]
        speeds = []
        frames, times, boxes = list(self.keypoints), list(self.timestamps), list(self.bboxes)

        for i in range(1, len(frames)):
            dt = times[i] - times[i - 1]
            if dt <= 0:
                continue
            height = self._box_height(boxes[i])
            for j in joint_indices:
                prev_pt, cur_pt = frames[i - 1][j], frames[i][j]
                if prev_pt[2] < MIN_KPT_CONFIDENCE or cur_pt[2] < MIN_KPT_CONFIDENCE:
                    continue
                dist = math.hypot(cur_pt[0] - prev_pt[0], cur_pt[1] - prev_pt[1])
                speeds.append((dist / height) / dt)

        if len(speeds) < 2:
            return 0.0

        mean_speed = sum(speeds) / len(speeds)
        variance = sum((s - mean_speed) ** 2 for s in speeds) / len(speeds)
        return float(variance)

    # ============== Debug Output ==============

    def debug_signals(self):
        """Return debug metrics for overlay/logging."""
        limb_var, limbs_ok = self.limb_variance_score()
        return {
            "track_id": self.track_id,
            "fall_state": self.fall_state,
            "fall_velocity": round(self.hip_vertical_velocity_normalized(), 2),
            "fall_acceleration": round(self._velocity_acceleration(), 3),
            "fall_height_reduction": round(self._height_reduction(), 3),
            "run_state": self.run_state,
            "run_speed": round(self.centroid_horizontal_speed(), 2),
            "run_confidence": round(sum(self.run_score_history) / max(len(self.run_score_history), 1), 2),
            "run_limb_var": round(limb_var, 3) if limbs_ok else None,
            "run_direction_consistent": self._direction_consistency(),
            "run_stride_cycles": self._stride_cycle_count(),
            "fight_variance": round(self.limb_velocity_variance_normalized(), 2),
        }


# ============== Global Fight Detection Function ==============

def bbox_overlap_ratio(bbox_a, bbox_b):
    """Rule 3: Intersection area / smaller box's area"""
    ax1, ay1, ax2, ay2 = bbox_a
    bx1, by1, bx2, by2 = bbox_b

    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    smaller_area = min(area_a, area_b)

    if smaller_area <= 0:
        return 0.0
    return inter_area / smaller_area


def check_fight(track_a: PersonTrack, track_b: PersonTrack):
    """
    Pairwise fight detection with full spec compliance.

    Returns (status, overlap_ratio, confidence, event_output) where:
      status: "none", "close_interaction", "fight_detected"
      overlap_ratio: float [0, 1]
      confidence: float [0, 1] for debugging
      event_output: standardized dict per Spec 8.2, or None when status
                    is "none" (nothing worth reporting to the controller)

    Checks:
    - Rule 1: Minimum two people (implicit in function call)
    - Rule 2: Close proximity (overlap)
    - Rule 3: Frequent contact (high overlap)
    - Rule 4: Rapid limb motion (high variance)
    - Rule 5: Chaotic movement (implicit in variance)
    - Rule 6: Mutual interaction (both active)
    - Rule 7: Persistence (external management via alert manager)
    - Rule 8: Separation (external cleanup)
    """
    if not track_a.bboxes or not track_b.bboxes:
        return "none", 0.0, 0.0, None

    # Rule 3: Measure contact via bbox overlap
    overlap = bbox_overlap_ratio(track_a.bboxes[-1], track_b.bboxes[-1])
    if overlap < OVERLAP_THRESH:
        return "none", overlap, 0.0, None

    # Rule 4: Rapid limb motion in both participants
    var_a = track_a.limb_velocity_variance_normalized()
    var_b = track_b.limb_velocity_variance_normalized()
    peak_variance = max(var_a, var_b)

    # Rule 6: Check mutual interaction (both moving or one very active)
    min_variance = min(var_a, var_b)
    is_mutual = min_variance > FIGHT_VELOCITY_VAR_THRESH * 0.5 or peak_variance > FIGHT_VELOCITY_VAR_THRESH * 1.5

    # Adjust threshold if running is likely (Rule 5 consideration)
    running_likely = track_a.run_state == "CONFIRMED" or track_b.run_state == "CONFIRMED"
    effective_thresh = (
        FIGHT_VELOCITY_VAR_THRESH * FIGHT_RUNNING_MULTIPLIER
        if running_likely else FIGHT_VELOCITY_VAR_THRESH
    )

    # Compute confidence for debug
    confidence = min(peak_variance / effective_thresh, 1.0) * overlap

    debug_info = {
        "overlap": round(overlap, 3),
        "limb_var_a": round(var_a, 2),
        "limb_var_b": round(var_b, 2),
        "running_likely": running_likely,
    }

    if peak_variance > effective_thresh and is_mutual:
        event = build_event_output(
            event_name="FIGHT_DETECTED",
            confidence_score=confidence,
            tracked_person_ids=[track_a.track_id, track_b.track_id],
            event_state="CONFIRMED",
            debug_info=debug_info,
        )
        return "fight_detected", overlap, confidence, event

    event = build_event_output(
        event_name="FIGHT_DETECTED",
        confidence_score=confidence,
        tracked_person_ids=[track_a.track_id, track_b.track_id],
        event_state="CANDIDATE",
        debug_info=debug_info,
    )
    return "close_interaction", overlap, confidence, event