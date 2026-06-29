# app/exceptions/custom.py
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.logging import logger

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

# Relocated from app/core/exceptions.py to consolidate the system
async def database_integrity_exception_handler(request: Request, exc: IntegrityError):
    """Catches low-level database constraints (e.g. duplicate keys) globally."""
    logger.error(f"Database Integrity Violation Intercepted: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "DatabaseIntegrityError",
            "detail": "Data operational conflict. This entry might already exist."
        }
    )