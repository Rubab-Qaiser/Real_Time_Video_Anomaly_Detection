from datetime import datetime

from database.database import db


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    camera_id = db.Column(
        db.Integer,
        db.ForeignKey("cameras.id"),
        nullable=True,
    )

    detection_type = db.Column(
        db.String(50),
        nullable=False,
    )

    confidence = db.Column(
        db.Float,
        nullable=False,
    )

    severity = db.Column(
        db.String(20),
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        default="Active",
        nullable=False,
    )

    frame_path = db.Column(
        db.String(500),
        nullable=True,
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )

    camera = db.relationship(
        "Camera",
        backref="incidents",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "camera": self.camera.name if self.camera else "Unknown Camera",
            "location": self.camera.location if self.camera else "Unknown Location",
            "detection_type": self.detection_type,
            "confidence": self.confidence,
            "severity": self.severity,
            "status": self.status,
            "frame_path": getattr(self, "frame_path", None),
            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),
        }
