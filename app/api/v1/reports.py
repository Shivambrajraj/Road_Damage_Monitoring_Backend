from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.report import ReportResponse, ReportCreateResponse
from app.services.report_service import report_service

router = APIRouter()

@router.post("", response_model=ReportCreateResponse)
async def submit_report(
    latitude: float = Form(None),
    longitude: float = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await report_service.process_and_save_report(db, image, latitude, longitude, current_user)

@router.get("", response_model=list[ReportResponse])
def list_reports(
    type: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Regular users see only their own reports. Admins see all of them."""
    return report_service.get_reports(db, current_user, damage_type=type, severity=severity)

@router.get("/details/{report_id}", response_model=ReportResponse)
def get_report_details(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = report_service.get_report_by_id(db, report_id, current_user)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    if report == "forbidden":
        raise HTTPException(status_code=403, detail="You can only view your own reports.")
    return report
from app.dependencies.permissions import verify_admin_privileges

@router.get("/admin/all", response_model=list[ReportResponse])
def list_all_reports_admin(
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_privileges),
):
    """Admin-only: every report from every user, no filtering by owner."""
    return report_service.get_reports(db, admin_user)