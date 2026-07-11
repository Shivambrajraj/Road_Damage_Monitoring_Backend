# app/models/otp.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from app.core.database import Base


class EmailOTP(Base):
    """
    Stores one-time-passcodes issued to an email address for a given
    purpose (e.g. "register"). Only the bcrypt hash of the code is
    stored — never the plaintext — so a leaked DB row can't be used
    to sign in.
    """
    __tablename__ = "email_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    purpose = Column(String, nullable=False, default="register")  # "register" | "reset_password"
    otp_hash = Column(String, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))