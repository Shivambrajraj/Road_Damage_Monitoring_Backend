# app/api/v1/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.report import ReportResponse
from app.services.dashboard_service import dashboard_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aggregate counters for the dashboard's stat cards."""
    return dashboard_service.get_stats(db)


@router.get("/reports", response_model=List[ReportResponse])
def get_all_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches the entire history of road damage reports.
    Secured: Only accessible by logged-in users.
    Kept for backward compatibility — the dashboard page itself now
    uses GET /reports (via useReports) for the report list, and this
    /stats endpoint for the summary counters.
    """
    from app.utils.report_serializer import serialize_report
    reports = dashboard_service.get_dashboard_reports(db)
    return [serialize_report(r) for r in reports]
