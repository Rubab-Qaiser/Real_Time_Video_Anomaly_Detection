from flask import Blueprint, jsonify, request

from middleware.auth import viewer_required
from models.incident import Incident

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/", methods=["GET"])
@viewer_required
def get_logs():
    """
    Return live system logs derived from the incident database.
    """

    search = request.args.get("search", "").strip().lower()
    severity = request.args.get("severity")

    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()

    logs = []
    for incident in incidents:
        level = incident.severity.title()
        source = incident.camera.name if incident.camera else "Camera"
        message = f"{incident.detection_type} detected with {int(float(incident.confidence) * 100)}% confidence."

        item = {
            "id": incident.id,
            "timestamp": incident.timestamp.isoformat() if incident.timestamp else None,
            "type": "AI",
            "level": level,
            "source": source,
            "message": message,
        }

        if severity and severity != "All" and item["level"] != severity:
            continue

        if search and not (
            search in item["message"].lower()
            or search in item["source"].lower()
            or search in item["type"].lower()
        ):
            continue

        logs.append(item)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    start = (page - 1) * per_page
    end = start + per_page
    page_items = logs[start:end]

    return jsonify({
        "items": page_items,
        "total": len(logs),
        "page": page,
        "per_page": per_page,
        "pages": max((len(logs) + per_page - 1) // per_page, 1),
    })