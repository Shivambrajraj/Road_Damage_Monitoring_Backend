# app/exceptions/reports.py
from fastapi import status
from app.exceptions.custom import AppException

class InvalidImageException(AppException):
    def __init__(self, detail: str = "Uploaded file format is corrupt or unsupported."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ReportNotFoundException(AppException):
    def __init__(self, detail: str = "The requested road report identifier does not exist."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)