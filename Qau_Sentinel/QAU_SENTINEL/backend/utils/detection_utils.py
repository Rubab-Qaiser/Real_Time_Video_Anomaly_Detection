import cv2

CLASS_COLORS = {
    "Fire": (0, 0, 255),          # Red
    "Smoke": (0, 255, 255),       # Yellow
    "Crowd": (255, 140, 0),       # Orange
}


def draw_detections(frame, detections):
    """
    Draw detection bounding boxes and labels
    onto an OpenCV frame.
    """

    for detection in detections:

        x1, y1, x2, y2 = detection["bbox"]

        value = float(detection['confidence'])
        if value <= 1.0:
            value *= 100.0
        label = (
            f"{detection['class']} "
            f"{int(round(value))}%"
        )

        color = CLASS_COLORS.get(
            detection["class"],
            (0, 255, 0),
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2,
        )

        cv2.rectangle(
            frame,
            (x1, y1 - 30),
            (x2, y1),
            color,
            -1,
        )

        cv2.putText(
            frame,
            label,
            (x1 + 8, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    return frame