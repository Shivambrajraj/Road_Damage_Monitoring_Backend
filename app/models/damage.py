# app/models/damage.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Damage(Base):
    __tablename__ = "damages"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False)  # "pothole" or "crack"
    confidence = Column(Float, nullable=False)  # AI accuracy percentage

    # Link back to the parent report record
    report = relationship("Report", back_populates="damages")