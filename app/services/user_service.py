# app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import user_repository
from app.core.security import SecurityManager
from app.exceptions.users import UserAlreadyExistsException # Import our clean custom exception

class UserService:
    @staticmethod
    def register_new_user(db: Session, user_in: UserCreate) -> User:
        # Check for conflicts using custom exceptions
        if user_repository.get_by_username(db, username=user_in.username):
            raise UserAlreadyExistsException(detail="This username is already taken.")

        if user_repository.get_by_email(db, email=user_in.email):
            raise UserAlreadyExistsException(detail="This email address is already taken.")

        hashed_pwd = SecurityManager.hash_password(user_in.password)

        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_pwd,
            is_active=True,
            is_admin=False
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

user_service = UserService()