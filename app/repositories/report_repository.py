# app/repositories/report_repository.py
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.report import Report

class ReportRepository(BaseRepository[Report]):
    def __init__(self):
        super().__init__(Report)

    def create_report(
        self, db: Session, *, image_path: str, damage_category: str, latitude: float | None, longitude: float | None
    ) -> Report:
        db_obj = Report(
            image_path=image_path,
            damage_category=damage_category,
            latitude=latitude,
            longitude=longitude
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_all_by_newest(self, db: Session):
        return db.query(self.model).order_by(self.model.id.desc()).all()

    def get_filtered(self, db: Session, *, damage_type: str | None = None, severity: str | None = None):
        query = db.query(self.model)
        if damage_type:
            query = query.filter(self.model.damage_category.ilike(f"%{damage_type}%"))
        if severity:
            query = query.filter(self.model.severity_level.ilike(severity))
        return query.order_by(self.model.id.desc()).all()

report_repository = ReportRepository()