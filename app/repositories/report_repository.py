# app/repositories/report_repository.py
import sys
import os
from sqlalchemy.orm import Session
from app.models.report import Report

class ReportRepository:
    def __init__(self):
        self.model = Report

    def get_filtered(
        self, 
        db: Session, 
        *, 
        damage_type: str | None = None, 
        severity: str | None = None, 
        status: str | None = None, 
        owner_id: int | None = None
    ) -> list[Report]:
        """
        Dynamically filters road damage reports based on provided search vectors.
        Returns results sorted by newest records first.
        """
        query = db.query(self.model)
        
        if damage_type:
            query = query.filter(self.model.damage_category.ilike(f"%{damage_type}%"))
        if severity:
            query = query.filter(self.model.severity_level.ilike(severity))
        if status:
            query = query.filter(self.model.status == status)
        if owner_id is not None:
            query = query.filter(self.model.reported_by_id == owner_id)
            
        return query.order_by(self.model.id.desc()).all()

    def update_status(self, db: Session, report_id: int, new_status: str) -> Report | None:
        """
        Updates the workflow state of a damage report and attaches an explicit UTC timestamp.
        """
        from datetime import datetime, timezone
        
        report = db.query(self.model).filter(self.model.id == report_id).first()
        if report is None:
            return None
            
        report.status = new_status
        report.status_updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(report)
        return report

# Instantiate the repository object cleanly at the end of the file block
report_repository = ReportRepository()