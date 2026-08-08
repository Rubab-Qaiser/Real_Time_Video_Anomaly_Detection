from flask import Blueprint, request, jsonify, Response
from datetime import datetime, timezone

from middleware.auth import token_required, admin_required, operator_required, viewer_required
from services.camera_service import camera_service
from services.stream_service import stream_service
from socket_events import broadcast_camera_status, socketio

# ✅ Remove url_prefix - it's added in app.py
camera_bp = Blueprint("cameras", __name__)


# ====================== GET ALL ======================
@camera_bp.get("/")
@viewer_required
def get_cameras():
    search = request.args.get("search", "").strip()
    status = request.args.get("status")
    cameras = camera_service.get_all(search=search, status=status)

    # Keep the camera management page focused on the four primary feeds.
    if len(cameras) > 4:
        cameras = cameras[:4]

    return jsonify({
        "items": cameras,
        "total": len(cameras)
    })


# ====================== GET ONE ======================
@camera_bp.get("/<int:id>")
@viewer_required
def get_camera(id):
    camera = camera_service.get_by_id(id)
    if not camera:
        return jsonify({"error": "Camera not found"}), 404
    return jsonify(camera)


# ====================== CREATE ======================
@camera_bp.post("/")
@operator_required
def create_camera():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Camera name is required"}), 400

    camera = camera_service.create(data)
    broadcast_camera_status(camera["id"], "online", camera)
    return jsonify(camera), 201


# ====================== UPDATE ======================
@camera_bp.put("/<int:id>")
@operator_required
def update_camera(id):
    data = request.get_json()
    camera = camera_service.update(id, data)
    if not camera:
        return jsonify({"error": "Camera not found"}), 404
    if "status" in data:
        broadcast_camera_status(id, data["status"], camera)
    return jsonify(camera)


# ====================== DELETE ======================
@camera_bp.delete("/<int:id>")
@admin_required
def delete_camera(id):
    success = camera_service.delete(id)
    if not success:
        return jsonify({"error": "Camera not found"}), 404
    socketio.emit("camera_deleted", {
        "camera_id": id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return jsonify({"message": "Camera deleted successfully"}), 200


# ====================== STREAM ALIAS ======================
@camera_bp.get("/<int:id>/stream")
def stream_alias(id):
    return live_stream(id)


# ====================== LIVE STREAM ======================
@camera_bp.get("/<int:id>/live")
def live_stream(id):
    """
    Live stream endpoint - authenticates via token in URL or header.
    camera_service.open() always returns True (even without a real
    source) so the MJPEG stream stays alive and serves placeholder
    frames when the source is unavailable.
    """
    from utils.jwt_utils import verify_access_token

    # Try to get token from query parameter first (for <img> tag)
    token = request.args.get("token")

    # If not in query, try Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return jsonify({"error": "Authorization required"}), 401

    # Verify token
    user_id, error = verify_access_token(token)
    if error:
        return jsonify({"error": error}), 401

    # Open camera if not already open, then start streaming.
    try:
        if not camera_service.is_open(id):
            camera_service.open(id)

        # Broadcast online status so the dashboard UI updates immediately.
        # NOTE: use "Online" (capitalized) to match the DB value and the
        # CameraCard statusConfig keys ("Online"/"Offline"/"Maintenance").
        camera_data = camera_service.get_by_id(id)
        broadcast_camera_status(id, "Online", camera_data)

        return Response(
            stream_service.generate_stream(camera_id=id),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        print(f"❌ Stream error for camera {id}: {e}")
        return jsonify({"error": f"Stream error: {str(e)}"}), 500
