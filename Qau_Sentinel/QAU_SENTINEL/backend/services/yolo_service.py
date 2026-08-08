from random import randint, uniform


class YOLOService:
    """
    Detection service.

    This currently returns mock detections so the
    backend and frontend can be developed without
    the trained YOLO model.

    Later this class will load the actual model and
    perform inference without changing any API code.
    """

    def __init__(self):
        self.model = None
        self.model_loaded = False

    def load_model(self):
        """
        Placeholder model loader.

        Later:
            self.model = YOLO(Config.YOLO_MODEL)
        """

        self.model_loaded = True

    def detect(self, frame):
        """
        Returns detections for a frame.

        Output format is final and should not change
        after integrating the real model.
        """

        if not self.model_loaded:
            self.load_model()

        height, width = frame.shape[:2]

        detections = []

        if randint(0, 3) == 0:

            detections.append(
                {
                    "class": "Fire",
                    "confidence": round(
                        uniform(0.70, 0.98),
                        2,
                    ),
                    "bbox": [
                        int(width * 0.15),
                        int(height * 0.20),
                        int(width * 0.45),
                        int(height * 0.70),
                    ],
                }
            )

        if randint(0, 4) == 0:

            detections.append(
                {
                    "class": "Smoke",
                    "confidence": round(
                        uniform(0.65, 0.95),
                        2,
                    ),
                    "bbox": [
                        int(width * 0.50),
                        int(height * 0.15),
                        int(width * 0.85),
                        int(height * 0.60),
                    ],
                }
            )

        if randint(0, 2) == 0:

            detections.append(
                {
                    "class": "Crowd",
                    "confidence": round(
                        uniform(0.80, 0.99),
                        2,
                    ),
                    "bbox": [
                        int(width * 0.25),
                        int(height * 0.45),
                        int(width * 0.75),
                        int(height * 0.95),
                    ],
                }
            )

        return detections


yolo_service = YOLOService()