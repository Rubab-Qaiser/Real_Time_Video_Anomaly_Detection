import cv2
import time
import numpy as np
from services.camera_service import camera_service


class StreamService:
    def _build_placeholder_frame(self, camera_id):
        """Create a lightweight placeholder frame when a camera source is unavailable."""
        frame = np.full((480, 640, 3), (15, 23, 42), dtype=np.uint8)
        cv2.putText(frame, f"Camera {camera_id}", (40, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, "Unavailable", (40, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (220, 220, 220), 2)
        return frame

    def _encode_frame(self, frame):
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            return None
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n'
                b'Content-Length: ' + str(len(jpeg)).encode() + b'\r\n'
                b'\r\n' + jpeg.tobytes() + b'\r\n')

    def generate_stream(self, camera_id):
        """Generate MJPEG stream for a camera.
        
        The camera is already opened by the live_stream endpoint before
        calling this function, so we don't need to open it again here.
        If frames are temporarily unavailable, placeholder frames are
        served to keep the MJPEG stream alive in the browser.
        """
        consecutive_failures = 0
        placeholder_count = 0
        max_placeholders = 600  # ~5 minutes of placeholders before giving up

        while True:
            frame = camera_service.read_frame(camera_id)
            if frame is None:
                consecutive_failures += 1
                placeholder_count += 1
                
                # If we've been serving placeholders for too long, stop
                if placeholder_count >= max_placeholders:
                    print(f"❌ Stream {camera_id}: Too many consecutive failures, stopping stream")
                    return
                
                frame = self._build_placeholder_frame(camera_id)
                
                # If we've had too many failures, slow down the retry rate
                if consecutive_failures > 10:
                    time.sleep(1.0)
                else:
                    time.sleep(0.5)
            else:
                consecutive_failures = 0
                placeholder_count = 0

            encoded = self._encode_frame(frame)
            if encoded is None:
                time.sleep(0.1)
                continue

            yield encoded
            time.sleep(0.033)  # ~30 FPS


stream_service = StreamService()