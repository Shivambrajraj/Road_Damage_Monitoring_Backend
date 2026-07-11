# app/services/admin_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.report import Report
from app.repositories.user_repository import user_repository


class AdminService:
    @staticmethod
    def get_platform_stats(db: Session) -> dict:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_admins = db.query(func.count(User.id)).filter(User.is_admin.is_(True)).scalar() or 0
        total_reports = db.query(func.count(Report.id)).scalar() or 0
        high_severity_reports = (
            db.query(func.count(Report.id)).filter(func.lower(Report.severity_level) == "high").scalar() or 0
        )
        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_reports": total_reports,
            "high_severity_reports": high_severity_reports,
        }

    @staticmethod
    def list_users(db: Session) -> list[User]:
        return db.query(User).order_by(User.id.desc()).all()

    @staticmethod
    def set_user_active(db: Session, user_id: int, is_active: bool, acting_admin: User) -> User:
        target = user_repository.get_by_id(db, user_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if target.id == acting_admin.id and not is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't deactivate your own account.")
        target.is_active = is_active
        db.add(target)
        db.commit()
        db.refresh(target)
        return target

    @staticmethod
    def set_user_admin(db: Session, user_id: int, is_admin: bool, acting_admin: User) -> User:
        target = user_repository.get_by_id(db, user_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if target.id == acting_admin.id and not is_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't remove your own admin access.")
        target.is_admin = is_admin
        db.add(target)
        db.commit()
        db.refresh(target)
        return target


admin_service = AdminService()