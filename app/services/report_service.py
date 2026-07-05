# app/services/report_service.py
from app.repositories.report_repository import report_repository

class ReportService:
    @staticmethod
    async def process_and_save_report(db, image, latitude, longitude, current_user):
        # ... your existing image file processing/saving logic ...
        
        db_report = report_repository.create_report(
            db=db,
            image_path=file_location,
            damage_category=summary_category,
            latitude=latitude,
            longitude=longitude,
            reported_by_id=current_user.id,
        )
        return db_report

    @staticmethod
    def get_reports(db, current_user, damage_type=None, severity=None):
        owner_id = None if current_user.is_admin else current_user.id
        reports = report_repository.get_filtered(db, damage_type=damage_type, severity=severity, owner_id=owner_id)
        return [serialize_report(r) for r in reports]

    @staticmethod
    def get_report_by_id(db, report_id, current_user):
        report = report_repository.get_by_id(db, report_id)
        if report is None:
            return None
        if not current_user.is_admin and report.reported_by_id != current_user.id:
            return "forbidden"
        return serialize_report(report)

# Instantiate the service object
report_service = ReportService()