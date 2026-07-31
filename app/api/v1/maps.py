# app/api/v1/maps.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.report_repository import report_repository
from app.utils.report_serializer import serialize_report

router = APIRouter()


@router.get("/markers")
def get_map_markers(db: Session = Depends(get_db)):
    """
    Returns all reports (across all users) that have GPS coordinates, for
    plotting on the Leaflet map (MapPage.jsx -> MapView.jsx / MarkerPopup.jsx).

    NOTE: previously this called report_service.get_reports(db) without the
    required `current_user` argument, which raised a TypeError on every
    request -> the frontend silently caught the failed request and always
    rendered "No geo-tagged detections yet", even when GPS-tagged reports
    existed. The map is a shared, all-users hazard view, so we query the
    repository directly (owner_id=None) rather than routing through the
    per-user-scoped service method.
    """
    reports = report_repository.get_filtered(db)
    serialized = [serialize_report(r) for r in reports]
    return [r for r in serialized if r["latitude"] is not None and r["longitude"] is not None]
