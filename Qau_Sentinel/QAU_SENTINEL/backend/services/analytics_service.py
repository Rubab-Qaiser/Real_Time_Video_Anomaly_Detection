from sqlalchemy import func
from datetime import datetime, timedelta

from database.database import db
from models.incident import Incident
from models.camera import Camera


class AnalyticsService:
    """
    Handles analytics calculations for the dashboard.
    """

    def get_dashboard_stats(self):
        """Return high-level dashboard statistics."""
        total_cameras = Camera.query.count()

        active_incidents = Incident.query.filter(
            Incident.status == "Active"
        ).count()

        resolved_incidents = Incident.query.filter(
            Incident.status == "Resolved"
        ).count()

        total_incidents = Incident.query.count()

        # Average confidence across all incidents
        avg_confidence = db.session.query(
            func.avg(Incident.confidence)
        ).scalar() or 0.0

        return {
            "total_cameras": total_cameras,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "total_incidents": total_incidents,
            "average_confidence": round(float(avg_confidence), 1),
            "ai_accuracy": round(float(avg_confidence), 1),   # Same as confidence for now
        }

    def get_detection_distribution(self):
        """Count incidents grouped by detection type."""
        results = (
            db.session.query(
                Incident.detection_type,
                func.count(Incident.id).label("count"),
            )
            .group_by(Incident.detection_type)
            .all()
        )

        return {detection_type: count for detection_type, count in results}

    def get_incident_trends(self):
        """Return weekly and monthly trends from REAL database data."""
        now = datetime.utcnow()

        # --- Weekly: Last 7 days, grouped by day-name + detection_type ---
        week_ago = now - timedelta(days=7)
        weekly_rows = (
            db.session.query(
                func.date(Incident.timestamp).label("day_date"),
                Incident.detection_type,
                func.count(Incident.id).label("count"),
            )
            .filter(Incident.timestamp >= week_ago)
            .group_by(func.date(Incident.timestamp), Incident.detection_type)
            .all()
        )

        # Build a lookup: {day_name: {detection_type: count}}
        weekly_lookup = {}
        for row in weekly_rows:
            if row.day_date is None:
                continue
            # func.date() returns a string in SQLite, e.g. "2024-01-15"
            day_str = str(row.day_date)
            try:
                day_dt = datetime.strptime(day_str, "%Y-%m-%d")
                day_name = day_dt.strftime("%a")
            except (ValueError, TypeError):
                continue
            if day_name not in weekly_lookup:
                weekly_lookup[day_name] = {}
            weekly_lookup[day_name][row.detection_type] = (
                weekly_lookup[day_name].get(row.detection_type, 0) + row.count
            )

        # Build ordered day list (last 7 days)
        day_names = []
        for i in range(6, -1, -1):
            day_names.append((now - timedelta(days=i)).strftime("%a"))

        # Collect all detection types present
        all_types = set()
        for day_data in weekly_lookup.values():
            all_types.update(day_data.keys())

        weekly = []
        for day in day_names:
            entry = {"day": day}
            day_data = weekly_lookup.get(day, {})
            for dtype in all_types:
                entry[dtype] = day_data.get(dtype, 0)
            weekly.append(entry)

        # --- Monthly: Last 30 days, grouped by week ---
        month_ago = now - timedelta(days=30)
        monthly_rows = (
            db.session.query(
                func.date(Incident.timestamp).label("day_date"),
                Incident.detection_type,
                func.count(Incident.id).label("count"),
            )
            .filter(Incident.timestamp >= month_ago)
            .group_by(func.date(Incident.timestamp), Incident.detection_type)
            .all()
        )

        # Group by ISO week number
        monthly_lookup = {}
        for row in monthly_rows:
            if row.day_date is None:
                continue
            day_str = str(row.day_date)
            try:
                day_dt = datetime.strptime(day_str, "%Y-%m-%d")
                iso_week = day_dt.isocalendar()[1]
            except (ValueError, TypeError):
                continue
            label = f"Week {iso_week}"
            if label not in monthly_lookup:
                monthly_lookup[label] = {}
            monthly_lookup[label][row.detection_type] = \
                monthly_lookup[label].get(row.detection_type, 0) + row.count

        monthly_types = set()
        for week_data in monthly_lookup.values():
            monthly_types.update(week_data.keys())

        monthly = []
        for label in sorted(monthly_lookup.keys()):
            entry = {"month": label}
            week_data = monthly_lookup[label]
            for dtype in monthly_types:
                entry[dtype] = week_data.get(dtype, 0)
            monthly.append(entry)

        return {
            "weekly": weekly,
            "monthly": monthly,
        }

    def get_camera_performance(self):
        """Return incident count and real AVG confidence per camera."""
        results = (
            db.session.query(
                Camera.id,
                Camera.name,
                Camera.location,
                func.count(Incident.id).label("incidents"),
                func.avg(Incident.confidence).label("avg_confidence"),
            )
            .outerjoin(Incident, Camera.id == Incident.camera_id)
            .group_by(Camera.id, Camera.name, Camera.location)
            .all()
        )

        return [
            {
                "id": cam.id,
                "camera": cam.name or f"Camera {cam.id}",
                "location": cam.location or "Unknown",
                "uptime": 98,  # TODO: Add real uptime tracking (needs camera heartbeats)
                "incidents": cam.incidents,
                "confidence": round(float(cam.avg_confidence or 0), 1),
            }
            for cam in results
        ]

    def get_recent_reports(self, limit=10):
        """Return the most recent incidents as reports."""
        reports = (
            Incident.query.order_by(
                Incident.timestamp.desc()
            )
            .limit(limit)
            .all()
        )

        return [report.to_dict() for report in reports]


# Singleton instance
analytics_service = AnalyticsService()