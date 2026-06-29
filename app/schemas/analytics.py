# app/schemas/analytics.py
from pydantic import BaseModel
from typing import Dict, List


class SeverityBreakdown(BaseModel):
    low: int
    medium: int
    high: int


class TrendPoint(BaseModel):
    month: str
    count: int


class DamageSummary(BaseModel):
    """Matches the shape AnalyticsPage.jsx expects:
    { severity: {low, medium, high}, trends: [{month, count}, ...] }"""
    severity: SeverityBreakdown
    trends: List[TrendPoint]
