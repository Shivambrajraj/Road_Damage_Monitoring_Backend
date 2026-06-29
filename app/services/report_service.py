# app/services/report_service.py
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.report_repository import report_repository
from app.models.damage import Damage
from app.ml.preprocessing.image_preprocessing import ImagePreprocessor
from app.ml.inference.detect import run_damage_detection
from app.ml.inference.classify import SeverityClassifier
from app.utils.file_manager import FileManager
from app.utils.image_processor import ImageProcessor
from app.utils.report_serializer import serialize_report

UPLOAD_DIR = "app/storage/uploads/original"


class ReportService:
    @staticmethod
    async def process_and_save_report(
        db: Session, image: UploadFile, latitude: float | None, longitude: float | None
    ):
        # 1. Save upload securely to disk storage structures
        file_location = await FileManager.save_uploaded_file(image, UPLOAD_DIR)
        ImageProcessor.validate_and_read_image(file_location)

        # 2. Preprocess the image to fit model constraints
        ImagePreprocessor.prepare_for_inference(file_location)

        # 3. Run damage detection (currently a structured mock — see
        #    app/ml/inference/detect.py for the Phase 2 real-model TODO)
        detections = run_damage_detection(file_location)

        # 4. Generate summary strings
        if detections:
            unique_categories = list(set([d["label"] for d in detections]))
            summary_category = ", ".join(unique_categories)
        else:
            summary_category = "Normal"

        # 5. Evaluate overall risk priority via our SeverityClassifier
        computed_severity = SeverityClassifier.calculate_priority_level(detections)

        # 6. Save the record using the Repository Layer
        db_report = report_repository.create_report(
            db=db,
            image_path=file_location,
            damage_category=summary_category,
            latitude=latitude,
            longitude=longitude
        )

        # Assign and save our new severity assessment column property fields
        db_report.severity_level = computed_severity

        for item in detections:
            damage_item = Damage(
                report_id=db_report.id,
                category=item["label"],
                confidence=item["confidence"]
            )
            db.add(damage_item)

        db.commit()
        db.refresh(db_report)

        # 7. Build the API response: base report fields + an immediate
        #    "detection" summary for the upload page to display right away.
        response = serialize_report(db_report)

        if detections:
            top = max(detections, key=lambda d: d["confidence"])
            response["detection"] = {
                "class_name": top["label"],
                "confidence": top["confidence"],
                "bounding_box": None,  # Phase 2: real model will provide real coordinates
            }
        else:
            response["detection"] = {
                "class_name": "Normal",
                "confidence": 1.0,
                "bounding_box": None,
            }

        return response

    @staticmethod
    def get_reports(db: Session, damage_type: str | None = None, severity: str | None = None):
        reports = report_repository.get_filtered(db, damage_type=damage_type, severity=severity)
        return [serialize_report(r) for r in reports]

    @staticmethod
    def get_report_by_id(db: Session, report_id: int):
        report = report_repository.get_by_id(db, report_id)
        if report is None:
            return None
        return serialize_report(report)


report_service = ReportService()
