from flask import Blueprint, jsonify, request

from middleware.auth import (
    viewer_required,
    operator_required,
)
from services.incident_service import incident_service

from socket_events import (
    broadcast_new_incident,
    broadcast_incident_update,
)

incident_bp = Blueprint(
    "incidents",
    __name__,
)


@incident_bp.route("/", methods=["GET"])  # ✅ Changed from .get to .route
@viewer_required
def get_incidents():
    """
    Get paginated incidents with optional
    search and filters.
    """

    page = request.args.get(
        "page",
        default=1,
        type=int,
    )

    per_page = request.args.get(
        "per_page",
        default=10,
        type=int,
    )

    search = request.args.get("search")
    detection_type = request.args.get("type")
    severity = request.args.get("severity")
    status = request.args.get("status")

    pagination = incident_service.get_all(
        page=page,
        per_page=per_page,
        search=search,
        detection_type=detection_type,
        severity=severity,
        status=status,
    )

    return jsonify(
        {
            "items": [
                incident.to_dict()
                for incident in pagination.items
            ],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "total": pagination.total,
        }
    )


@incident_bp.route("/<int:incident_id>", methods=["GET"])  # ✅ Changed
@viewer_required
def get_incident(incident_id):
    """
    Get a single incident.
    """

    incident = incident_service.get_by_id(
        incident_id
    )

    if incident is None:
        return (
            jsonify(
                {
                    "message": "Incident not found."
                }
            ),
            404,
        )

    return jsonify(
        incident.to_dict()
    )


# ====================== CREATE ======================

@incident_bp.route("/", methods=["POST"])  # ✅ Changed
@operator_required
def create_incident():
    """
    Create a new incident.
    """

    data = request.get_json()

    if not data or not data.get("camera_id"):
        return jsonify(
            {"error": "camera_id is required"}
        ), 400

    incident = incident_service.create(data)

    broadcast_new_incident(
        incident.to_dict()
    )

    return jsonify(
        incident.to_dict()
    ), 201


# ====================== UPDATE ======================

@incident_bp.route("/<int:incident_id>", methods=["PUT"])  # ✅ Changed
@operator_required
def update_incident(incident_id):
    """
    Update an existing incident.
    """

    incident = incident_service.get_by_id(
        incident_id
    )

    if incident is None:
        return (
            jsonify(
                {
                    "message": "Incident not found."
                }
            ),
            404,
        )

    data = request.get_json()

    updated = incident_service.update(
        incident,
        data,
    )

    if data and "status" in data:
        broadcast_incident_update(
            incident_id,
            data["status"],
            updated.to_dict(),
        )

    return jsonify(
        updated.to_dict()
    )


# ====================== DELETE ======================

@incident_bp.route("/<int:incident_id>", methods=["DELETE"])  # ✅ Changed
@operator_required
def delete_incident(incident_id):
    """
    Delete an incident.
    """

    incident = incident_service.get_by_id(
        incident_id
    )

    if incident is None:
        return (
            jsonify(
                {
                    "message": "Incident not found."
                }
            ),
            404,
        )

    incident_service.delete(
        incident
    )

    return jsonify(
        {
            "message": "Incident deleted successfully."
        }
    )