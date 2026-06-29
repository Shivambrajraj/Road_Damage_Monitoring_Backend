# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List
from app.schemas.report import ReportResponse

class DashboardOverview(BaseModel):
    total_incidents: int
    critical_hazards: int
    pending_notifications: int
    recent_activity: List[ReportResponse]

    class Config:
        from_attributes = True