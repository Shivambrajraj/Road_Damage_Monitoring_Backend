# app/repositories/otp_repository.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.otp import EmailOTP


class OTPRepository(BaseRepository[EmailOTP]):
    def __init__(self):
        super().__init__(EmailOTP)

    def create(self, db: Session, *, email: str, purpose: str, otp_hash: str, expires_at: datetime) -> EmailOTP:
        db_obj = EmailOTP(email=email, purpose=purpose, otp_hash=otp_hash, expires_at=expires_at)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_latest_active(self, db: Session, *, email: str, purpose: str) -> EmailOTP | None:
        """Most recent, unused, not-yet-expired OTP row for this email/purpose."""
        return (
            db.query(self.model)
            .filter(
                self.model.email == email,
                self.model.purpose == purpose,
                self.model.is_used.is_(False),
                self.model.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
            )
            .order_by(self.model.created_at.desc())
            .first()
        )

    def mark_used(self, db: Session, otp_row: EmailOTP) -> None:
        otp_row.is_used = True
        db.add(otp_row)
        db.commit()

    def increment_attempts(self, db: Session, otp_row: EmailOTP) -> None:
        otp_row.attempts += 1
        db.add(otp_row)
        db.commit()

    def invalidate_previous(self, db: Session, *, email: str, purpose: str) -> None:
        """Called before issuing a fresh OTP so old codes for the same email/purpose stop working."""
        db.query(self.model).filter(
            self.model.email == email,
            self.model.purpose == purpose,
            self.model.is_used.is_(False),
        ).update({"is_used": True})
        db.commit()


otp_repository = OTPRepository()