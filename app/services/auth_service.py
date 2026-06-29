# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import user_repository
from app.core.security import SecurityManager
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

        # 3. Issue signed JWT containing core safe identity scopes
        access_token = JWTManager.create_access_token(
            data={"sub": user.username, "is_admin": user.is_admin}
        )
        return TokenResponse(access_token=access_token, token_type="bearer")

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

        hashed = SecurityManager.hash_password(payload.password)
        user = user_repository.create_user(
            db, username=payload.username, email=payload.email, hashed_password=hashed
        )

        # Log the new user in immediately so the frontend gets a usable token
        access_token = JWTManager.create_access_token(
            data={"sub": user.username, "is_admin": user.is_admin}
        )
        return TokenResponse(access_token=access_token, token_type="bearer")

auth_service = AuthService()