# app/middleware/authorization.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class MaintenanceLockMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, system_lock: bool = False):
        super().__init__(app)
        self.system_lock = system_lock

    async def dispatch(self, request: Request, call_next):
        """Allows administrators to put endpoints into read-only mode during migration tasks."""
        if self.system_lock and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "success": False,
                    "error": "SystemLockout",
                    "detail": "Platform is undergoing scheduled infrastructure optimization. Writing actions are temporarily frozen."
                }
            )
        return await call_next(request)