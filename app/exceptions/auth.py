# app/exceptions/auth.py
from fastapi import status
from app.exceptions.custom import AppException

class CredentialsException(AppException):
    def __init__(self, detail: str = "Incorrect username or password."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class TokenExpiredException(AppException):
    def __init__(self, detail: str = "Session expired. Please log in again."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class PermissionDeniedException(AppException):
    def __init__(self, detail: str = "Access Denied: Insufficient security permissions."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)