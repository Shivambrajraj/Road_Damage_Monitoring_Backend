# app/services/auth_service.py
import jwt as pyjwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import user_repository
from app.core.security import SecurityManager
from app.core.config import settings
from app.utils.jwt import JWTManager
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, credentials: LoginRequest) -> TokenResponse:
        # 1. Look up user by username
        user = user_repository.get_by_username(db, username=credentials.username)

        # 2. Validate existence and password accuracy
        if not user or not SecurityManager.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Contact an administrator.",
            )

        # 3. Issue signed JWT containing core safe identity scopes
        access_token = JWTManager.create_access_token(
            data={"sub": user.username, "is_admin": user.is_admin}
        )
        return TokenResponse(
            access_token=access_token, token_type="bearer",
            username=user.username, is_admin=user.is_admin,
        )

    @staticmethod
    def _assert_email_was_otp_verified(email: str, verification_token: str) -> None:
        """
        Registration is gated behind the email OTP flow: the frontend must
        call /auth/send-otp then /auth/verify-otp first, and pass the
        resulting short-lived token here. This re-validates it server-side
        so the OTP step can't be skipped by calling /auth/register directly.
        """
        try:
            decoded = pyjwt.decode(
                verification_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except pyjwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification expired or is invalid. Please verify your email again.",
            )

        if decoded.get("purpose") != "email_verified" or decoded.get("sub") != email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification does not match this registration. Please verify again.",
            )

    @staticmethod
    def register_user(db: Session, payload: RegisterRequest) -> TokenResponse:
        # Reject duplicate usernames/emails up front with a clear message
        if user_repository.get_by_username(db, username=payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That username is already registered."
            )
        if user_repository.get_by_email(db, email=payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is already registered."
            )

        # Require proof that this email already passed the OTP challenge
        AuthService._assert_email_was_otp_verified(payload.email, payload.verification_token)

        hashed = SecurityManager.hash_password(payload.password)
        user = user_repository.create_user(
            db, username=payload.username, email=payload.email, hashed_password=hashed
        )
        user.is_verified = True
        db.add(user)
        db.commit()

        # Log the new user in immediately so the frontend gets a usable token
        access_token = JWTManager.create_access_token(
            data={"sub": user.username, "is_admin": user.is_admin}
        )
        return TokenResponse(
            access_token=access_token, token_type="bearer",
            username=user.username, is_admin=user.is_admin,
        )

auth_service = AuthService()