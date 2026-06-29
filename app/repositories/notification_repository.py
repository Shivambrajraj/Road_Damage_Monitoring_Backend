# app/repositories/notification_repository.py
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.notification import Notification

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self):
        super().__init__(Notification)

    def get_by_user(self, db: Session, user_id: int):
        """Fetches all system alerts for a specific user profile ordered by latest first."""
        return db.query(self.model).filter(self.model.user_id == user_id).order_by(self.model.id.desc()).all()

    def create_alert(self, db: Session, user_id: int, title: str, message: str) -> Notification:
        """Saves a brand new system event notice to the database tier."""
        alert = Notification(user_id=user_id, title=title, message=message)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

notification_repository = NotificationRepository()