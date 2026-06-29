# app/models/report.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    damage_category = Column(String, nullable=False)  # Summarized text (e.g., "Pothole, Crack")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    severity_level = Column(String, default="Low", nullable=False)

    # Add this line to map the link over to individual damage items
    damages = relationship("Damage", back_populates="report", cascade="all, delete-orphan")