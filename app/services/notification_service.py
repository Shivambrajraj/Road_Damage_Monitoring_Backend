# app/services/notification_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.notification_repository import notification_repository

class NotificationService:
    @staticmethod
    def get_user_notifications(db: Session, user_id: int):
        return notification_repository.get_by_user(db, user_id=user_id)

    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
        # Retrieve the alert entity using inherited base repository methods
        alert = notification_repository.get_by_id(db, id=notification_id)
        
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification alert not found.")
            
        if alert.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action context.")

        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return alert

notification_service = NotificationService()