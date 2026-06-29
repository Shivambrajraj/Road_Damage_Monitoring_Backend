# app/utils/response.py
from typing import Any
from fastapi.responses import JSONResponse

def create_api_response(status_code: int, message: str, data: Any = None) -> JSONResponse:
    """Wraps API data payloads inside a standardized system corporate response blueprint."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )
