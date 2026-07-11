# app/services/otp_service.py
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import email_manager
from app.core.security import SecurityManager
from app.repositories.otp_repository import otp_repository
from app.repositories.user_repository import user_repository
from app.utils.jwt import JWTManager

REGISTER_PURPOSE = "register"


class OTPService:
    @staticmethod
    def _generate_code() -> str:
        # 6-digit numeric code, cryptographically random (not random.randint)
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def send_registration_otp(db: Session, email: str) -> dict:
        # Don't let someone spam OTPs to an email that's already a full account
        if user_repository.get_by_email(db, email=email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is already registered. Try logging in instead.",
            )

        # Invalidate any still-active codes so only the newest one works
        otp_repository.invalidate_previous(db, email=email, purpose=REGISTER_PURPOSE)

        code = OTPService._generate_code()
        otp_hash = SecurityManager.hash_password(code)
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        )

        otp_repository.create(db, email=email, purpose=REGISTER_PURPOSE, otp_hash=otp_hash, expires_at=expires_at)
        email_manager.send_otp_email(email, code)

        return {
            "message": f"A verification code was sent to {email}.",
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
        }

    @staticmethod
    def verify_registration_otp(db: Session, email: str, otp: str) -> str:
        otp_row = otp_repository.get_latest_active(db, email=email, purpose=REGISTER_PURPOSE)

        if otp_row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active verification code for this email. Please request a new one.",
            )

        if otp_row.attempts >= settings.OTP_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many incorrect attempts. Please request a new code.",
            )

        if not SecurityManager.verify_password(otp, otp_row.otp_hash):
            otp_repository.increment_attempts(db, otp_row)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect verification code.",
            )

        otp_repository.mark_used(db, otp_row)

        # Short-lived token that proves "this email passed OTP" without
        # creating the account yet. /auth/register requires this token.
        verification_token = JWTManager.create_access_token(
            data={"sub": email, "purpose": "email_verified"},
            expires_delta=timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES),
        )
        return verification_token


otp_service = OTPService()