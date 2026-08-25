from flask import Flask, request, send_from_directory, jsonify
import os
import time
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from performance_metrics import PerformanceMetrics

from config import Config
from database.init_db import init_database

from api.health import health_bp
from api.cameras import camera_bp
from api.incidents import incident_bp
from api.detections import detection_bp
from api.analytics import analytics_bp
from api.logs import logs_bp
from api.users import users_bp
from api.auth import auth_bp

from socket_events import init_socketio

# ==========================================
# Socket.IO Instance
# ==========================================

socketio = None
performance_metrics = PerformanceMetrics(
    csv_path=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "system", "thesis_metrics.csv")
    )
)


def create_app():
    global socketio

    app = Flask(__name__)

    app.config.from_object(Config)
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Prevent redirect issues caused by trailing slashes
    app.url_map.strict_slashes = False

    # Initialize Database
    init_database(app)

    # ==========================================
    # CORS
    # ==========================================

    CORS(
        app,
        origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        supports_credentials=True,
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "X-Requested-With",
        ],
        methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        max_age=86400,
    )

    # ==========================================
    # Register API Blueprints
    # ==========================================

    app.register_blueprint(
        health_bp,
        url_prefix="/api",
    )

    app.register_blueprint(
        camera_bp,
        url_prefix="/api/cameras",
    )

    app.register_blueprint(
        detection_bp,
        url_prefix="/api/detections",
    )

    app.register_blueprint(
        incident_bp,
        url_prefix="/api/incidents",
    )

    app.register_blueprint(
        analytics_bp,
        url_prefix="/api/analytics",
    )

    app.register_blueprint(
        logs_bp,
        url_prefix="/api/logs",
    )

    app.register_blueprint(
        users_bp,
        url_prefix="/api/users",
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth",
    )

    # ==========================================
    # Socket.IO
    # ==========================================

    socketio = SocketIO(
        app,
        cors_allowed_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        async_mode="threading",
    )

    init_socketio(socketio)

    # ==========================================
    # Serve Alert Snapshot Images
    # ==========================================
    # __file__ = backend/app.py, go up 3 levels to reach AA/, then into system/Alerts/
    ALERTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "system", "Alerts")
    ALERTS_DIR = os.path.normpath(ALERTS_DIR)
    print(f"📁 ALERTS_DIR resolved to: {ALERTS_DIR}")
    if os.path.isdir(ALERTS_DIR):
        files = [f for f in os.listdir(ALERTS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
        print(f"📁 Found {len(files)} alert images in ALERTS_DIR")

    @app.route("/api/alerts/<path:filename>")
    def serve_alert_image(filename):
        """Serve alert snapshot images from the system/Alerts directory."""
        return send_from_directory(ALERTS_DIR, filename)

    @app.route("/api/metrics")
    def metrics_endpoint():
        """Expose thesis measurement snapshot for live monitoring and reporting."""
        return jsonify(performance_metrics.get_snapshot()), 200

    return app, socketio


app, socketio = create_app()


# ==========================================
# Socket.IO Events
# ==========================================

@socketio.on("connect")
def handle_connect():
    sid = getattr(request, "sid", None)

    print(f"🔌 Client connected: {sid}")

    emit(
        "connected",
        {
            "message": "Connected to Socket.IO server",
        },
    )


@socketio.on("disconnect")
def handle_disconnect():
    sid = getattr(request, "sid", None)

    print(f"🔌 Client disconnected: {sid}")


@socketio.on("join_room")
def handle_join_room(data):
    room = data.get("room")

    if room:
        join_room(room)

        sid = getattr(request, "sid", None)

        print(
            f"📢 Client {sid} joined room: {room}"
        )


@socketio.on("leave_room")
def handle_leave_room(data):
    room = data.get("room")

    if room:
        leave_room(room)

        sid = getattr(request, "sid", None)

        print(
            f"📢 Client {sid} left room: {room}"
        )


@socketio.on("latency_ping")
def handle_latency_ping(data):
    """Respond to client latency pings with server timestamp to measure RTT."""
    try:
        client_ts = data.get("client_ts")
    except Exception:
        client_ts = None

    server_ts = int(time.time() * 1000)
    emit("latency_pong", {"client_ts": client_ts, "server_ts": server_ts})

    if client_ts is not None:
        try:
            rtt_ms = (time.time() * 1000) - float(client_ts)
            performance_metrics.record_socket_rtt(rtt_ms)
        except Exception:
            pass


# ==========================================
# Run Application
# ==========================================

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True,
    )