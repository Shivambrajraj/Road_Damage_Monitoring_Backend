# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import user_repository
from app.repositories.audit_repository import audit_repository # Import your audit logger
from app.core.security import SecurityManager
from app.utils.jwt import JWTManager
from app.schemas.auth import LoginRequest, TokenResponse

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, credentials: LoginRequest) -> TokenResponse:
        user = user_repository.get_by_username(db, username=credentials.username)
        
        if not user or not SecurityManager.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # SUCCESSFUL FOOTPRINT LOGGING: Record the audit trail item
        audit_repository.log_action(
            db=db,
            user_id=user.id,
            action="USER_LOGIN",
            description=f"User {user.username} successfully authenticated via web console api."
        )
        
        access_token = JWTManager.create_access_token(
            data={"sub": user.username, "is_admin": user.is_admin}
        )
        return TokenResponse(access_token=access_token, token_type="bearer")

print("AuthService audit footprint tracing mounted successfully.")
auth_service = AuthService()