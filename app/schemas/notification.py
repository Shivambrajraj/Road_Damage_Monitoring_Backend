# app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    timestamp: datetime

    class Config:
        from_attributes = True