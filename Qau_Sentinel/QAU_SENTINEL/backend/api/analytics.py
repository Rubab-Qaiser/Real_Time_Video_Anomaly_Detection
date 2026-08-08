import csv
import io
import os
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from middleware.auth import viewer_required

from services.analytics_service import analytics_service
from services.incident_service import incident_service

analytics_bp = Blueprint(
    "analytics",
    __name__,
)


# ==========================================
# Export helpers
# ==========================================

def _generate_csv(incidents):
    """Generate CSV in memory from a list of incident dicts."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Timestamp", "Camera", "Location",
        "Detection Type", "Confidence", "Severity", "Status",
    ])

    for inc in incidents:
        writer.writerow([
            inc.get("id"),
            inc.get("timestamp"),
            inc.get("camera"),
            inc.get("location"),
            inc.get("detection_type") or inc.get("type"),
            inc.get("confidence"),
            inc.get("severity"),
            inc.get("status"),
        ])

    output.seek(0)
    return io.BytesIO(output.getvalue().encode("utf-8"))


def _generate_pdf(incidents):
    """
    Generate a simple text-based PDF-replacement using
    plain text with report layout. For a proper PDF,
    install `reportlab` or `weasyprint`.
    """
    lines = []
    lines.append("=" * 72)
    lines.append("  QAU Sentinel — Incident Report")
    lines.append(f"  Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("=" * 72)
    lines.append("")

    for inc in incidents:
        lines.append(f"  ID:          {inc.get('id')}")
        lines.append(f"  Timestamp:   {inc.get('timestamp')}")
        lines.append(f"  Camera:      {inc.get('camera')}")
        lines.append(f"  Location:    {inc.get('location')}")
        lines.append(f"  Type:        {inc.get('detection_type') or inc.get('type')}")
        lines.append(f"  Confidence:  {inc.get('confidence')}%")
        lines.append(f"  Severity:    {inc.get('severity')}")
        lines.append(f"  Status:      {inc.get('status')}")
        lines.append("-" * 72)

    text = "\n".join(lines)
    return io.BytesIO(text.encode("utf-8"))


# ==========================================
# Existing endpoints
# ==========================================

@analytics_bp.route("/dashboard", methods=["GET"])
@viewer_required
def dashboard_stats():
    """Dashboard overview statistics."""
    return jsonify(
        analytics_service.get_dashboard_stats()
    )


@analytics_bp.route("/distribution", methods=["GET"])
@viewer_required
def detection_distribution():
    """Detection type distribution."""
    return jsonify(
        analytics_service.get_detection_distribution()
    )


@analytics_bp.route("/trends", methods=["GET"])
@viewer_required
def incident_trends():
    """Incident trends over time."""
    return jsonify(
        analytics_service.get_incident_trends()
    )


@analytics_bp.route("/camera-performance", methods=["GET"])
@viewer_required
def camera_performance():
    """Camera performance analytics."""
    return jsonify(
        analytics_service.get_camera_performance()
    )


@analytics_bp.route("/reports", methods=["GET"])
@viewer_required
def recent_reports():
    """Recent incident reports."""
    return jsonify(
        analytics_service.get_recent_reports()
    )


@analytics_bp.route("/overview", methods=["GET"])
@viewer_required
def analytics_overview():
    """Combined analytics endpoint."""
    return jsonify(
        {
            "dashboard": analytics_service.get_dashboard_stats(),
            "distribution": analytics_service.get_detection_distribution(),
            "trends": analytics_service.get_incident_trends(),
            "camera_performance": analytics_service.get_camera_performance(),
            "reports": analytics_service.get_recent_reports(),
        }
    )


# ==========================================
# Export endpoints
# ==========================================

@analytics_bp.route("/export/csv", methods=["GET"])
@viewer_required
def export_csv():
    """Export incidents as CSV."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 1000, type=int)

    pagination = incident_service.get_all(page=page, per_page=per_page)
    incidents = [inc.to_dict() for inc in pagination.items]

    buf = _generate_csv(incidents)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    return send_file(
        buf,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"incidents_report_{timestamp}.csv",
    )


@analytics_bp.route("/export/pdf", methods=["GET"])
@viewer_required
def export_pdf():
    """Export incidents as a text-based report (PDF-style)."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 1000, type=int)

    pagination = incident_service.get_all(page=page, per_page=per_page)
    incidents = [inc.to_dict() for inc in pagination.items]

    buf = _generate_pdf(incidents)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"incidents_report_{timestamp}.txt",
    )
