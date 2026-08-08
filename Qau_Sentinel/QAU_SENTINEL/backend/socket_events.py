from datetime import datetime, timezone
from flask_socketio import emit

# SocketIO instance will be set from app.py
socketio = None


def init_socketio(socketio_instance):
    """Initialize socketio instance from app.py."""
    global socketio
    socketio = socketio_instance


def broadcast_camera_status(camera_id, status, camera_data=None):
    """Broadcast camera status update to all clients."""
    if socketio:
        socketio.emit("camera_status", {
            "camera_id": camera_id,
            "status": status,
            "camera": camera_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


def broadcast_new_detection(detection_data):
    """Broadcast new detection to all clients."""
    if socketio:
        socketio.emit("new_detection", {
            "detection": detection_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


def broadcast_new_incident(incident_data):
    """Broadcast new incident to all clients."""
    if socketio:
        socketio.emit("new_incident", {
            "incident": incident_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


def broadcast_incident_update(incident_id, status, incident_data=None):
    """Broadcast incident status update to all clients."""
    if socketio:
        socketio.emit("incident_update", {
            "incident_id": incident_id,
            "status": status,
            "incident": incident_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


def broadcast_new_log(log_data):
    """Broadcast new log entry to all clients."""
    if socketio:
        socketio.emit("new_log", {
            "log": log_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })