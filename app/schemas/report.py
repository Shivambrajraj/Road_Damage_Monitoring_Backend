# app/schemas/report.py
from pydantic import BaseModel
from typing import Optional


class DetectionInfo(BaseModel):
    """Shape expected by the frontend's <DetectionResult /> component."""
    class_name: str
    confidence: float
    bounding_box: Optional[list] = None


class ReportResponse(BaseModel):
    """
    Field names here intentionally match the frontend's existing
    components (ReportTable, ReportCard, MarkerPopup, ReportDetailsPage)
    rather than the internal DB column names — id is a string (frontend
    calls .substring() on it), type/severity/created_at/image_url are
    the camelCase-free, frontend-facing aliases for damage_category /
    severity_level / timestamp / image_path.
    """
    id: str
    type: str
    severity: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: str
    image_url: str
    confidence: Optional[float] = None


class ReportCreateResponse(ReportResponse):
    """Returned only from POST /reports — includes the immediate detection
    result so the upload page can show it right away."""
    detection: Optional[DetectionInfo] = None
