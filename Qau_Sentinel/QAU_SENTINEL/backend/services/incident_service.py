from sqlalchemy import or_

from database.database import db
from models.incident import Incident


class IncidentService:
    """
    Handles incident database operations.
    """

    def get_all(
        self,
        page=1,
        per_page=10,
        search=None,
        detection_type=None,
        severity=None,          # ✅ Added
        status=None,
    ):
        """
        Get paginated incidents with optional
        search and filters.
        """
        query = Incident.query

        if detection_type:
            query = query.filter(
                Incident.detection_type == detection_type
            )

        # ✅ New severity filter
        if severity:
            query = query.filter(
                Incident.severity == severity
            )

        if status:
            query = query.filter(
                Incident.status == status
            )

        if search:
            query = query.filter(
                or_(
                    Incident.severity.ilike(f"%{search}%"),
                    Incident.detection_type.ilike(f"%{search}%"),
                )
            )

        query = query.order_by(
            Incident.timestamp.desc()
        )

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    def get_by_id(self, incident_id):
        """
        Return a single incident.
        """
        return Incident.query.get(incident_id)

    def create(self, data):
        """
        Create a new incident.
        """
        incident = Incident()

        incident.camera_id = data.get("camera_id")
        incident.detection_type = data.get("detection_type") or "Unknown"
        # Normalize confidence to the project-wide percentage scale (0-100).
        conf_raw = data.get("confidence") or 0.0
        try:
            conf_val = float(conf_raw)
        except Exception:
            conf_val = 0.0
        if conf_val <= 1.0:
            conf_val = conf_val * 100.0
        incident.confidence = max(0.0, min(100.0, conf_val))
        incident.severity = data.get("severity") or "medium"
        incident.status = data.get("status", "Open")
        incident.frame_path = data.get("frame_path")

        db.session.add(incident)
        db.session.commit()

        return incident

    def update(self, incident, data):
        """
        Update an existing incident.
        """
        if "camera_id" in data:
            incident.camera_id = data["camera_id"]

        if "detection_type" in data:
            incident.detection_type = data["detection_type"]

        if "confidence" in data:
            try:
                conf_val = float(data["confidence"]) if data["confidence"] is not None else 0.0
            except Exception:
                conf_val = 0.0
            if conf_val <= 1.0:
                conf_val = conf_val * 100.0
            incident.confidence = max(0.0, min(100.0, conf_val))

        if "severity" in data:
            incident.severity = data["severity"]

        if "status" in data:
            incident.status = data["status"]

        db.session.commit()

        return incident

    def delete(self, incident):
        """
        Delete an incident.
        """
        db.session.delete(incident)
        db.session.commit()


incident_service = IncidentService()