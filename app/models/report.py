from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    damage_category = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    severity_level = Column(String, default="Low", nullable=False)

    # NEW: who filed this report (nullable so old rows don't break)
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    damages = relationship("Damage", back_populates="report", cascade="all, delete-orphan")
    reporter = relationship("User")