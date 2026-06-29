# app/dependencies/permissions.py
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.dependencies.auth import get_current_user

def verify_admin_privileges(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures that the current authenticated user has administrative
    clearance before allowing them to access a route.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Administrative authorization is required."
        )
    return current_user