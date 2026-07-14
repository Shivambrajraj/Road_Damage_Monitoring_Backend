# app/schemas/report.py
from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal

REPORT_STATUSES = Literal["pending", "verified", "in_progress", "resolved", "rejected"]


class DetectionInfo(BaseModel):
    class_name: str
    confidence: float
    bounding_box: Optional[list] = None


class ReportResponse(BaseModel):
    id: str
    type: str
    severity: str
    status: str = "pending"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: str
    image_url: str
    confidence: Optional[float] = None


class ReportCreateResponse(ReportResponse):
    detection: Optional[DetectionInfo] = None


class ReportStatusUpdate(BaseModel):
    status: REPORT_STATUSES