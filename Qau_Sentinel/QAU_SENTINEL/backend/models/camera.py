from datetime import datetime

from database.database import db


class Camera(db.Model):
    __tablename__ = "cameras"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    location = db.Column(
        db.String(150),
        nullable=False,
    )

    source = db.Column(
        db.String(255),
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        default="Online",
        nullable=False,
    )

    fps = db.Column(
        db.Integer,
        default=30,
        nullable=False,
    )

    resolution = db.Column(
        db.String(20),
        default="1920x1080",
        nullable=False,
    )

    ai_status = db.Column(
        db.String(50),
        default="Active",
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "source": self.source,
            "status": self.status,
            "fps": self.fps,
            "resolution": self.resolution,
            "ai_status": self.ai_status,
            "created_at": self.created_at.isoformat(),
        }
