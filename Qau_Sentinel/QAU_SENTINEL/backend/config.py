import os
from datetime import timedelta


class Config:
    # ============= FLASK =============
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
    PORT = int(os.environ.get("FLASK_PORT", 5000))

    # ============= DATABASE =============
    # Absolute path to the backend directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Absolute path to database/ai_surveillance.db
    DB_PATH = os.path.join(
        BASE_DIR,
        "database",
        "ai_surveillance.db",
    )

    # SQLAlchemy connection string
    DATABASE_URL = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{DB_PATH}"
    )

    # ============= CORS =============
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:4173",
    ).split(",")

    # ============= JWT =============
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY")
        or "dev-jwt-secret-key-32-chars-long!!"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_ALGORITHM = "HS256"

    # ============= YOLO =============
    YOLO_MODEL = os.environ.get(
        "YOLO_MODEL",
        "yolov8n.pt",
    )

    # ============= CAMERA =============
    CAMERA_SOURCE = os.environ.get(
        "CAMERA_SOURCE",
        "0",
    )