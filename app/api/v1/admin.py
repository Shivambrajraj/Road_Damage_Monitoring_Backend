# app/api/v1/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.dependencies.permissions import verify_admin_privileges
from app.services.admin_service import admin_service

router = APIRouter()

@router.get("/stats")
def platform_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_privileges),
):
    """Admin-only: platform-wide counters for the admin dashboard cards."""
    return admin_service.get_platform_stats(db)

@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_privileges),
):
    """Admin-only: every registered user."""
    return admin_service.list_users(db)

@router.patch("/users/{user_id}/active", response_model=UserResponse)
def set_user_active(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_privileges),
):
    """Admin-only: activate/deactivate a user account (blocks their login)."""
    return admin_service.set_user_active(db, user_id, is_active, admin_user)

@router.patch("/users/{user_id}/admin", response_model=UserResponse)
def set_user_admin(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_privileges),
):
    """Admin-only: grant/revoke admin privileges for a user."""
    return admin_service.set_user_admin(db, user_id, is_admin, admin_user)