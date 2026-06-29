# app/repositories/audit_repository.py
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.audit_log import AuditLog

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def log_action(self, db: Session, user_id: int | None, action: str, description: str) -> AuditLog:
        """Saves an immutable security action footprint entry to the database."""
        log_entry = AuditLog(user_id=user_id, action=action, description=description)
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

audit_repository = AuditRepository()