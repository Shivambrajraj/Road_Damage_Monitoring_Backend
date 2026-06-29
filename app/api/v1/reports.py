# app/api/v1/reports.py
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.report import ReportResponse, ReportCreateResponse
from app.services.report_service import report_service

router = APIRouter()


@router.post("", response_model=ReportCreateResponse)
async def submit_report(
    latitude: float = Form(None),
    longitude: float = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Create a new road damage report from an uploaded image."""
    return await report_service.process_and_save_report(db, image, latitude, longitude)


@router.get("", response_model=list[ReportResponse])
def list_reports(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all reports, optionally filtered by damage type and/or severity."""
    return report_service.get_reports(db, damage_type=type, severity=severity)


@router.get("/details/{report_id}", response_model=ReportResponse)
def get_report_details(report_id: int, db: Session = Depends(get_db)):
    """Fetch a single report by ID for the report details page."""
    report = report_service.get_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
