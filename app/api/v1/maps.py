# app/api/v1/maps.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.report_service import report_service

router = APIRouter()


@router.get("/markers")
def get_map_markers(db: Session = Depends(get_db)):
    """
    Returns all reports that have GPS coordinates, for plotting on
    the Leaflet map (MapPage.jsx -> MapView.jsx / MarkerPopup.jsx).
    """
    reports = report_service.get_reports(db)
    return [r for r in reports if r["latitude"] is not None and r["longitude"] is not None]
