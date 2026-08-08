import sys
import os
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app import app
from database.database import db
from models.incident import Incident
from models.camera import Camera


def seed_new_incidents():
    with app.app_context():
        try:
            # Get existing cameras
            cameras = Camera.query.all()
            if not cameras:
                print("❌ No cameras found. Please seed cameras first.")
                print("   Run: python seed_cameras.py")
                return

# Check if incidents already exist
            existing = Incident.query.count()

            if existing > 0:
                print(f"⚠️  {existing} incidents already exist. Skipping seed.")
                return

            # Sample incidents — include ALL types including Fire, Smoke, Crowd
            incidents = [
                # Original types
                {
                    "camera_id": cameras[0].id,
                    "detection_type": "Fire",
                    "confidence": 94,
                    "severity": "critical",
                    "status": "Open",
                },
                {
                    "camera_id": cameras[1].id if len(cameras) > 1 else cameras[0].id,
                    "detection_type": "Smoke",
                    "confidence": 87,
                    "severity": "high",
                    "status": "Investigating",
                },
                {
                    "camera_id": cameras[2].id if len(cameras) > 2 else cameras[0].id,
                    "detection_type": "Crowd",
                    "confidence": 76,
                    "severity": "medium",
                    "status": "Active",
                },
                # New types
                {
                    "camera_id": cameras[0].id,
                    "detection_type": "Fall",
                    "confidence": 92,
                    "severity": "critical",
                    "status": "Open",
                },
                {
                    "camera_id": cameras[1].id if len(cameras) > 1 else cameras[0].id,
                    "detection_type": "Running",
                    "confidence": 85,
                    "severity": "high",
                    "status": "Investigating",
                },
                {
                    "camera_id": cameras[2].id if len(cameras) > 2 else cameras[0].id,
                    "detection_type": "Fight",
                    "confidence": 94,
                    "severity": "critical",
                    "status": "Open",
                },
                {
                    "camera_id": cameras[3].id if len(cameras) > 3 else cameras[0].id,
                    "detection_type": "Unwanted Object",
                    "confidence": 78,
                    "severity": "high",
                    "status": "Resolved",
                },
            ]

            for data in incidents:
                incident = Incident()
                incident.camera_id = data["camera_id"]
                incident.detection_type = data["detection_type"]
                incident.confidence = data["confidence"]
                incident.severity = data["severity"]
                incident.status = data["status"]
                # ❌ REMOVED: incident.location = data["location"]
                # Location comes from the camera association
                db.session.add(incident)

            db.session.commit()
            print(f"✅ Added {len(incidents)} sample incidents with new types!")
            print("   Types added: Fall, Running, Fight, Unwanted Object")
            print("   Location will be pulled from the associated camera.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding incidents: {e}")


if __name__ == "__main__":
    seed_new_incidents()