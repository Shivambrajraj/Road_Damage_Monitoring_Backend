# app/services/report_service.py
from app.core.constants import DEFAULT_STORAGE_PATH
from app.repositories.report_repository import report_repository
from app.services.ml_service import MLService
from app.utils.file_manager import FileManager
from app.utils.image_processor import ImageProcessor
from app.utils.report_serializer import serialize_report

class ReportService:
    @staticmethod
    async def create_report(db, file, user, damage_type, severity, latitude=None, longitude=None):
        """
        Full upload pipeline:
          1. Persist the uploaded image to disk.
          2. Validate it's a real, decodable image.
          3. Run it through the YOLO detection model.
          4. Store the Report (+ any detected Damage rows) in the DB.
          5. Return the serialized report plus the top detection for the UI.
        """
        # 1. Save the raw upload to app/storage/uploads/original
        image_path = await FileManager.save_uploaded_file(file, DEFAULT_STORAGE_PATH)

        # 2. Make sure it's actually a valid image (raises InvalidImageException if not)
        ImageProcessor.validate_and_read_image(image_path)

        # 3. Run ML inference (never throws — returns an "error" key on failure instead)
        ml_result = MLService.analyze_road_image(image_path)
        detections = ml_result.get("detections", [])

        # 4. Persist the report row, plus one Damage row per detected object
        report = report_repository.create(
            db,
            image_path=image_path,
            damage_category=damage_type,
            severity_level=severity,
            latitude=latitude,
            longitude=longitude,
            reported_by_id=user.id,
            detections=detections,
        )

        # 5. Shape the response: base report fields + the single strongest detection
        response = serialize_report(report)
        if detections:
            top = max(detections, key=lambda d: d["confidence"])
            response["detection"] = {
                "class_name": top["label"],
                "confidence": top["confidence"],
                "bounding_box": top.get("bounding_box"),
            }
        return response

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