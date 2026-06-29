# app/api/v1/notifications.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.notification import NotificationResponse
from app.services.notification_service import notification_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def fetch_my_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieves an authenticated user's current array list of alerts and messages."""
    return notification_service.get_user_notifications(db, user_id=current_user.id)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def toggle_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Flags a specific system notification identifier as read."""
    return notification_service.mark_notification_as_read(db, notification_id, user_id=current_user.id)