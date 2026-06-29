# app/services/analytics_service.py
from collections import OrderedDict
from sqlalchemy.orm import Session
from app.repositories.report_repository import report_repository

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class AnalyticsService:
    @staticmethod
    def get_system_metrics(db: Session) -> dict:
        reports = report_repository.get_all_by_newest(db)

        severity_counts = {"low": 0, "medium": 0, "high": 0}
        for r in reports:
            level = (r.severity_level or "low").lower()
            if level in severity_counts:
                severity_counts[level] += 1

        # Group by calendar month across all reports (chronological order)
        monthly_counts = OrderedDict()
        for r in reports:
            if not r.timestamp:
                continue
            key = (r.timestamp.year, r.timestamp.month)
            monthly_counts[key] = monthly_counts.get(key, 0) + 1

        trends = [
            {"month": MONTH_LABELS[month - 1], "count": count}
            for (year, month), count in sorted(monthly_counts.items())
        ]

        return {
            "severity": severity_counts,
            "trends": trends,
        }


analytics_service = AnalyticsService()
