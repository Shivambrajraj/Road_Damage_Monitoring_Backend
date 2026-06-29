# app/exceptions/users.py
from fastapi import status
from app.exceptions.custom import AppException

class UserAlreadyExistsException(AppException):
    def __init__(self, detail: str = "An account with these credentials already exists."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)