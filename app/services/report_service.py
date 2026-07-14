# app/services/report_service.py
from app.repositories.report_repository import report_repository
from app.utils.report_serializer import serialize_report

class ReportService:
    @staticmethod
    def get_reports(db, current_user, damage_type=None, severity=None, status=None):
        owner_id = None if current_user.is_admin else current_user.id
        reports = report_repository.get_filtered(
            db, damage_type=damage_type, severity=severity, status=status, owner_id=owner_id
        )
        return [serialize_report(r) for r in reports]

    @staticmethod
    def get_report_by_id(db, report_id, current_user):
        report = db.query(report_repository.model).filter(report_repository.model.id == report_id).first()
        if report is None:
            return None
        if not current_user.is_admin and report.reported_by_id != current_user.id:
            return "forbidden"
        return serialize_report(report)

    @staticmethod
    def update_status(db, report_id, new_status):
        report = report_repository.update_status(db, report_id, new_status)
        if report is None:
            return None
        return serialize_report(report)

# Instantiate the service object cleanly at the base tail scope
report_service = ReportService()