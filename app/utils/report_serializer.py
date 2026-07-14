# app/utils/report_serializer.py
"""
Single source of truth for converting a `Report` DB row into the
JSON shape the frontend actually consumes (see ReportTable.jsx,
ReportCard.jsx, MarkerPopup.jsx, ReportDetailsPage.jsx).

DB column names stay as they are (damage_category, severity_level,
timestamp, image_path) — only the API-facing representation changes.
"""
import os
from app.core.config import settings
from app.models.report import Report


def serialize_report(report: Report) -> dict:
    # Average confidence across this report's detected damages (if any),
    # used for the "Model Confidence" display on ReportDetailsPage.
    confidences = [d.confidence for d in (report.damages or [])]
    avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else None

    # Build an absolute URL so the image renders correctly from the
    # frontend (which runs on a different origin/port than the API).
    filename = os.path.basename(report.image_path)
    image_url = f"{settings.BACKEND_BASE_URL}/static/{filename}"

    return {
        "id": str(report.id),
        "type": report.damage_category,
        "severity": (report.severity_level or "low").lower(),
        "status": report.status or "pending",
        "latitude": report.latitude,
        "longitude": report.longitude,
        "created_at": report.timestamp.isoformat() if report.timestamp else None,
        "image_url": image_url,
        "confidence": avg_confidence,
    }
