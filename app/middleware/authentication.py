# app/middleware/authentication.py
import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class GlobalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Attaches a quick authentication snapshot flag to request.state."""
        auth_header = request.headers.get("Authorization")
        request.state.is_authenticated = False
        request.state.username = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                request.state.is_authenticated = True
                request.state.username = payload.get("sub")
            except jwt.PyJWTError:
                pass  # Let route guards handle strict blocking actions later

        return await call_next(request)