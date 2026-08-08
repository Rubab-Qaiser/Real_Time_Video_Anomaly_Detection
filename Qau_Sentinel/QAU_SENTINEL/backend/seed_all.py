"""
Comprehensive seed script — recreates DB, users, cameras, and incidents.
Run this ONLY after the Flask backend is already running (it connects to the live DB).
"""
import sys
import os
from datetime import datetime, timedelta, timezone

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Force database path to be the same one the running Flask server uses
from config import Config
from database.database import db
from models.user import User
from models.camera import Camera
from models.incident import Incident
from flask import Flask

# Create a minimal Flask app just to get the DB context
app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = Config.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    # 1. Create all tables
    db.create_all()
    print("✅ Tables created / verified")

    # 2. Seed Users
    if User.query.count() > 0:
        print(f"⚠️  {User.query.count()} users already exist. Skipping.")
    else:
        admin = User()
        admin.username = "admin"
        admin.email = "admin@qau.edu.pk"
        admin.role = "Admin"
        admin.active = True
        admin.set_password("admin123")
        db.session.add(admin)

        operator = User()
        operator.username = "operator1"
        operator.email = "operator1@qau.edu.pk"
        operator.role = "Operator"
        operator.active = True
        operator.set_password("operator123")
        db.session.add(operator)

        viewer = User()
        viewer.username = "viewer1"
        viewer.email = "viewer1@qau.edu.pk"
        viewer.role = "Viewer"
        viewer.active = True
        viewer.set_password("viewer123")
        db.session.add(viewer)

        db.session.commit()
        print("✅ 3 users seeded (admin / operator1 / viewer1)")

    # 3. Seed Cameras
    if Camera.query.count() > 0:
        print(f"⚠️  {Camera.query.count()} cameras already exist. Skipping.")
    else:
        cameras_data = [
            {"name": "Main Entrance", "location": "Gate A", "source": "0", "status": "Online", "fps": 30, "resolution": "1920x1080", "ai_status": "Active"},
            {"name": "Parking Lot", "location": "North Wing", "source": "0", "status": "Online", "fps": 25, "resolution": "1280x720", "ai_status": "Active"},
            {"name": "Corridor B", "location": "Building B", "source": "0", "status": "Online", "fps": 20, "resolution": "1920x1080", "ai_status": "Idle"},
            {"name": "Server Room", "location": "Data Center", "source": "0", "status": "Maintenance", "fps": 30, "resolution": "2560x1440", "ai_status": "Active"},
        ]
        for c in cameras_data:
            cam = Camera()
            cam.name = c["name"]
            cam.location = c["location"]
            cam.source = c["source"]
            cam.status = c["status"]
            cam.fps = c["fps"]
            cam.resolution = c["resolution"]
            cam.ai_status = c["ai_status"]
            db.session.add(cam)
        db.session.commit()
        print(f"✅ {len(cameras_data)} cameras seeded")

    # 4. Seed Incidents
    if Incident.query.count() > 0:
        print(f"⚠️  {Incident.query.count()} incidents already exist. Skipping.")
    else:
        cameras = Camera.query.all()
        if not cameras:
            print("❌ No cameras found — cannot seed incidents.")
        else:
            now = datetime.now(timezone.utc)
            # Map detection types to available alert images in system/Alerts/
            # __file__ = backend/seed_all.py, go up 3 levels to reach AA/, then into system/Alerts/
            alerts_base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "system", "Alerts"))
            type_to_sample = {}
            if os.path.isdir(alerts_base):
                for f in sorted(os.listdir(alerts_base)):
                    if f.endswith('.png'):
                        parts = f.split('_')
                        if parts:
                            atype = parts[0]
                            if atype not in type_to_sample:
                                type_to_sample[atype] = f

            def get_frame_path(detection_type):
                """Map detection_type to a sample image filename."""
                type_map = {
                    "Fire": "fire", "Smoke": "fire", "Crowd": "crowd",
                    "Fall": "fall", "Running": "running", "Fight": "fight",
                    "Unwanted Object": "object_anomaly",
                }
                key = type_map.get(detection_type.lower().replace(" ", "_"), None)
                # Use any available image or None
                return f"Alerts/{type_to_sample.get(key, list(type_to_sample.values())[0])}" if type_to_sample else None

            incidents_data = [
                # Fire, Smoke, Crowd (original types)
                {"camera_id": cameras[0].id, "detection_type": "Fire", "confidence": 94, "severity": "critical", "status": "Open", "timestamp": now - timedelta(minutes=30)},
                {"camera_id": cameras[1].id if len(cameras) > 1 else cameras[0].id, "detection_type": "Smoke", "confidence": 87, "severity": "high", "status": "Investigating", "timestamp": now - timedelta(hours=1)},
                {"camera_id": cameras[2].id if len(cameras) > 2 else cameras[0].id, "detection_type": "Crowd", "confidence": 76, "severity": "medium", "status": "Active", "timestamp": now - timedelta(hours=2)},
                # New types
                {"camera_id": cameras[0].id, "detection_type": "Fall", "confidence": 92, "severity": "critical", "status": "Open", "timestamp": now - timedelta(hours=3)},
                {"camera_id": cameras[1].id if len(cameras) > 1 else cameras[0].id, "detection_type": "Running", "confidence": 85, "severity": "high", "status": "Investigating", "timestamp": now - timedelta(hours=4)},
                {"camera_id": cameras[2].id if len(cameras) > 2 else cameras[0].id, "detection_type": "Fight", "confidence": 94, "severity": "critical", "status": "Open", "timestamp": now - timedelta(hours=5)},
                {"camera_id": cameras[3].id if len(cameras) > 3 else cameras[0].id, "detection_type": "Unwanted Object", "confidence": 78, "severity": "high", "status": "Resolved", "timestamp": now - timedelta(hours=6)},
            ]
            for d in incidents_data:
                incident = Incident()
                incident.camera_id = d["camera_id"]
                incident.detection_type = d["detection_type"]
                incident.confidence = d["confidence"]
                incident.severity = d["severity"]
                incident.status = d["status"]
                incident.timestamp = d["timestamp"]
                incident.frame_path = get_frame_path(d["detection_type"])
                db.session.add(incident)
            db.session.commit()
            print(f"✅ {len(incidents_data)} incidents seeded (Fire, Smoke, Crowd, Fall, Running, Fight, Unwanted Object)")

    print("\n🎉 Seeding complete! Restart the Flask backend now.")
