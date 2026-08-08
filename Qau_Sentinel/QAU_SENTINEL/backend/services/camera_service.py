import threading
import time
import cv2
import os
import numpy as np
from database.database import db
from models.camera import Camera
from config import Config


# =============================================================================
# Helper: background frame reader thread
# =============================================================================

class _SourceReader:
    """
    Owns a single cv2.VideoCapture, reads frames in a tight loop, and stores
    the latest frame in a shared cache.  Multiple camera_ids can be mapped to
    the same _SourceReader (via reference counting).
    """

    def __init__(self, source_candidate, norm_source, demo_video_path=None):
        self.norm_source = norm_source
        self.demo_video_path = demo_video_path
        self.ref_count = 0
        self._cap = None
        self._thread = None
        self._stop = threading.Event()
        self._last_frame = None
        self._frame_lock = threading.Lock()
        self._failed_count = 0
        self._max_failures = 30  # ~3 seconds of failures before fallback

        # Try to open the requested source
        self._cap = self._try_open(source_candidate)

        # If it failed, try demo video
        if self._cap is None and demo_video_path:
            print(f"📹 Source '{norm_source}' unavailable, falling back to demo video: {demo_video_path}")
            self._cap = self._try_open(demo_video_path)

        if self._cap is not None:
            self._thread = threading.Thread(target=self._reader_loop, daemon=True, name=f"Reader-{norm_source}")
            self._thread.start()
            print(f"✅ Reader started for source '{norm_source}'")

    def _try_open(self, source):
        """Try to open a VideoCapture with fallback backends."""
        try:
            cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        except Exception:
            try:
                cap = cv2.VideoCapture(source)
            except Exception:
                return None
        if cap is not None and cap.isOpened():
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return cap
        return None

    def _reader_loop(self):
        """Background loop: reads frames as fast as possible, stores latest."""
        cap = self._cap
        if cap is None:
            return

        while not self._stop.is_set():
            if cap is not None:
                success, frame = cap.read()
                if success:
                    with self._frame_lock:
                        self._last_frame = frame
                        self._failed_count = 0
                else:
                    self._failed_count += 1
                    if self._failed_count >= self._max_failures:
                        cap.release()
                        cap = None
                        time.sleep(1.0)
                        cap = self._try_open_source()
                        self._cap = cap
                        self._failed_count = 0
                    else:
                        time.sleep(0.1)
            else:
                cap = self._try_open_source()
                self._cap = cap
                self._failed_count = 0
                time.sleep(0.1)

            time.sleep(0.016)  # ~60 fps max

        if cap is not None:
            cap.release()

    def _try_open_source(self):
        """Try to open demo video or webcam as fallback."""
        if self.demo_video_path:
            c = self._try_open(self.demo_video_path)
            if c is not None:
                return c
        return self._try_open(0)

    def get_frame(self):
        """Return the latest cached frame, or None if unavailable."""
        with self._frame_lock:
            if self._last_frame is not None:
                return self._last_frame.copy()
            return None

    def is_alive(self):
        """Check if the reader thread is running and producing frames."""
        return self._thread is not None and self._thread.is_alive()

    def stop(self):
        """Signal the reader thread to stop and release resources."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass


# =============================================================================
# CameraService
# =============================================================================

class CameraService:
    """
    Handles both database operations and camera streaming.

    Uses a frame-cache architecture: each unique source has exactly ONE
    background reader thread (_SourceReader) that continuously reads frames
    from the VideoCapture and stores the latest frame. All camera streams
    read from this cache, avoiding concurrent cap.read() calls.

    If the real source (e.g. webcam) is busy (e.g. held by the external
    detection pipeline), it falls back to a demo video file (Suho.mp4).
    """

    def __init__(self):
        self.cameras = {}  # camera_id -> True/False (tracking which are active)
        self.locks = {}    # camera_id -> threading.Lock (per-camera lock)

        # Active source readers: norm_source -> _SourceReader instance
        self._readers = {}
        self._readers_lock = threading.Lock()

        # Pre-compute fallback demo video path
        # __file__ = .../backend/services/camera_service.py
        # backend_dir = .../backend/  (go up TWO levels from services/)
        self._demo_video_path = None
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for f in ["Suho.mp4", "demo.mp4", "test.mp4"]:
            candidate = os.path.join(backend_dir, f)
            if os.path.isfile(candidate):
                self._demo_video_path = candidate
                break
        # Also try the system/ directory (one more level up from backend)
        project_dir = os.path.dirname(backend_dir)
        for f in ["Suho.mp4", "demo.mp4", "test.mp4"]:
            candidate = os.path.join(project_dir, f)
            if os.path.isfile(candidate):
                self._demo_video_path = candidate
                break

        if self._demo_video_path:
            print(f"📹 Demo video available: {self._demo_video_path}")
        else:
            print("📹 No demo video found (streams will show placeholder if webcam busy)")

    # ====================== DATABASE CRUD ======================

    def get_all(self, search=None, status=None):
        query = Camera.query
        if search:
            query = query.filter(
                (Camera.name.ilike(f"%{search}%")) |
                (Camera.location.ilike(f"%{search}%"))
            )
        if status and status.lower() != "all":
            query = query.filter_by(status=status.capitalize())
        cameras = query.all()
        return [camera.to_dict() for camera in cameras]

    def get_by_id(self, camera_id):
        camera = Camera.query.get(camera_id)
        return camera.to_dict() if camera else None

    def create(self, data):
        camera = Camera()
        camera.name = data.get("name")
        camera.location = data.get("location")
        camera.source = data.get("source")
        camera.status = data.get("status", "Offline")
        camera.fps = data.get("fps", 30)
        camera.resolution = data.get("resolution", "1920x1080")
        camera.ai_status = data.get("ai_status", "Active")
        db.session.add(camera)
        db.session.commit()
        return camera.to_dict()

    def update(self, camera_id, data):
        camera = Camera.query.get(camera_id)
        if not camera:
            return None
        if "name" in data:
            camera.name = data["name"]
        if "location" in data:
            camera.location = data["location"]
        if "source" in data:
            camera.source = data["source"]
        if "status" in data:
            camera.status = data["status"]
        db.session.commit()
        return camera.to_dict()

    def delete(self, camera_id):
        camera = Camera.query.get(camera_id)
        if not camera:
            return False
        db.session.delete(camera)
        db.session.commit()
        return True

    def _normalize_source(self, source):
        if not source:
            return "0"
        try:
            return str(int(source))
        except (ValueError, TypeError):
            return source

    # ====================== STREAMING ======================

    def _get_source_candidates(self, source):
        if not source:
            return [0]
        try:
            source_int = int(source)
            return [source_int, 0]
        except (ValueError, TypeError):
            return [source, 0]

    def open(self, camera_id):
        """
        Open camera stream for specific camera.
        Creates or shares a _SourceReader for the camera's source.
        Multiple cameras sharing the same source (e.g. "0") will all
        read from the same background reader thread.

        CRITICAL: Always returns True even if no source is available,
        so the MJPEG stream stays alive and serves placeholder frames.
        The reader thread continuously retries in the background.
        """
        if camera_id in self.cameras and self.cameras[camera_id]:
            return True

        camera_obj = Camera.query.get(camera_id)
        if not camera_obj:
            return False

        source = camera_obj.source
        norm_source = self._normalize_source(source)

        # === SHARED READER CHECK ===
        with self._readers_lock:
            if norm_source in self._readers:
                reader = self._readers[norm_source]
                reader.ref_count += 1
                self.cameras[camera_id] = True
                self.locks[camera_id] = threading.Lock()
                camera_obj.status = "Online"
                db.session.commit()
                print(f"✅ Camera {camera_id} sharing reader '{norm_source}' (ref_count={reader.ref_count})")
                return True

        # === CREATE NEW READER ===
        reader = None
        for candidate in self._get_source_candidates(source):
            reader = _SourceReader(candidate, norm_source, self._demo_video_path)
            if reader.is_alive():
                break
            reader = None

        if reader is None and self._demo_video_path:
            reader = _SourceReader(self._demo_video_path, norm_source, None)

        if reader is not None and reader.is_alive():
            with self._readers_lock:
                reader.ref_count = 1
                self._readers[norm_source] = reader
                self.cameras[camera_id] = True
                self.locks[camera_id] = threading.Lock()
            camera_obj.status = "Online"
            db.session.commit()
            print(f"✅ Camera {camera_id} opened with reader '{norm_source}'")
            return True
        else:
            if reader:
                reader.stop()

        # CRITICAL: Always mark as "open" even without a real source.
        # This ensures the MJPEG stream stays alive in the browser
        # and serves placeholder frames. The reader loop in stream_service
        # keeps the connection alive indefinitely.
        print(f"⚠️ Camera {camera_id}: No source available, serving placeholder frames")
        self.cameras[camera_id] = True
        self.locks[camera_id] = threading.Lock()
        return True

    def is_open(self, camera_id):
        return camera_id in self.cameras and self.cameras[camera_id] is not None

    def is_source_reader_alive(self, camera_id):
        camera_obj = Camera.query.get(camera_id)
        if not camera_obj:
            return False
        norm_source = self._normalize_source(camera_obj.source)
        with self._readers_lock:
            reader = self._readers.get(norm_source)
            return reader is not None and reader.is_alive() and reader.get_frame() is not None

    def read_frame(self, camera_id):
        """Read the latest cached frame from the background reader."""
        camera_obj = Camera.query.get(camera_id)
        if not camera_obj:
            return None

        norm_source = self._normalize_source(camera_obj.source)

        if camera_id not in self.locks:
            self.locks[camera_id] = threading.Lock()

        with self.locks[camera_id]:
            if not self.is_open(camera_id):
                if not self.open(camera_id):
                    return None

            with self._readers_lock:
                reader = self._readers.get(norm_source)

            if reader is None:
                return None

            # Just return the frame. If it's None, stream_service will
            # serve placeholder frames. Do NOT release the reader here
            # as it can race with other cameras sharing the same reader.
            frame = reader.get_frame()
            return frame

    def release(self, camera_id=None):
        """Release specific or all cameras.
        Only stops the background reader when NO cameras use it anymore.
        """
        if camera_id:
            if camera_id in self.cameras:
                del self.cameras[camera_id]
            if camera_id in self.locks:
                del self.locks[camera_id]

            camera_obj = Camera.query.get(camera_id)
            if camera_obj:
                norm_source = self._normalize_source(camera_obj.source)
                with self._readers_lock:
                    reader = self._readers.get(norm_source)
                    if reader:
                        reader.ref_count -= 1
                        if reader.ref_count <= 0:
                            reader.stop()
                            del self._readers[norm_source]
                            print(f"🔒 Stopped reader '{norm_source}' (no more cameras using it)")
                        else:
                            print(f"📡 Camera {camera_id} released from reader '{norm_source}', remaining refs: {reader.ref_count}")
        else:
            with self._readers_lock:
                for reader in self._readers.values():
                    reader.stop()
                self._readers.clear()
            self.cameras.clear()
            self.locks.clear()

    def get_status(self, camera_id=None):
        if camera_id:
            camera = Camera.query.get(camera_id)
            return {
                "id": camera_id,
                "connected": self.is_open(camera_id),
                "source": camera.source if camera else None,
                "reader_alive": self.is_source_reader_alive(camera_id) if camera else False,
            }
        return {"connected": bool(self.cameras)}


camera_service = CameraService()
