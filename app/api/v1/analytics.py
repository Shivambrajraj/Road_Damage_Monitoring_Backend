# app/api/v1/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.analytics import DamageSummary
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/summary", response_model=DamageSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Computes severity distribution and month-over-month report counts
    for the analytics page's charts.
    """
    return analytics_service.get_system_metrics(db)
