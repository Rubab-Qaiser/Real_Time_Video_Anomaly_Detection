import sys
import os

# Add backend to path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app import app
from database.database import db
from models.camera import Camera


def seed_cameras():
    with app.app_context():
        # Add sample cameras with unique FPS, Resolution, and AI Status
        cam1 = Camera()
        cam1.name = "Main Entrance"
        cam1.location = "Gate A"
        cam1.source = "0"
        cam1.status = "Online"
        cam1.fps = 30
        cam1.resolution = "1920x1080"
        cam1.ai_status = "Active"

        cam2 = Camera()
        cam2.name = "Library"
        cam2.location = "Floor 1"
        cam2.source = "0"
        cam2.status = "Online"
        cam2.fps = 25
        cam2.resolution = "1280x720"
        cam2.ai_status = "Active"

        cam3 = Camera()
        cam3.name = "Parking Area"
        cam3.location = "Block B"
        cam3.source = "0"
        cam3.status = "Online"
        cam3.fps = 20
        cam3.resolution = "1920x1080"
        cam3.ai_status = "Idle"

        cam4 = Camera()
        cam4.name = "Administration"
        cam4.location = "Reception"
        cam4.source = "0"
        cam4.status = "Online"
        cam4.fps = 30
        cam4.resolution = "2560x1440"
        cam4.ai_status = "Active"

        db.session.add(cam1)
        db.session.add(cam2)
        db.session.add(cam3)
        db.session.add(cam4)

        db.session.commit()
        print(" 4 sample cameras added successfully!")


if __name__ == "__main__":
    seed_cameras()