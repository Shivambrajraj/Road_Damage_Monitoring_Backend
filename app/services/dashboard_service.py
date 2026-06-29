# app/services/dashboard_service.py
from sqlalchemy.orm import Session
from app.repositories.report_repository import report_repository


class DashboardService:
    @staticmethod
    def get_dashboard_reports(db: Session):
        # Business rules for dashboard visibility can go here later
        return report_repository.get_all_by_newest(db)

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Matches the shape DashboardPage.jsx expects:
        { total_anomalies, high_severity, system_health }"""
        reports = report_repository.get_all_by_newest(db)
        total_anomalies = len(reports)
        high_severity = sum(1 for r in reports if (r.severity_level or "").lower() == "high")

        return {
            "total_anomalies": total_anomalies,
            "high_severity": high_severity,
            "system_health": "100%",
        }


dashboard_service = DashboardService()
