# app/middleware/rate_limit.py
import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Tracks request timestamps per client IP address
        self.client_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Filter out timestamps older than 60 seconds
        self.client_records[client_ip] = [
            t for t in self.client_records[client_ip] if current_time - t < 60
        ]

        # Check if the rate threshold is breached
        if len(self.client_records[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "RateLimitExceeded",
                    "detail": "Too many requests. Please slow down and try again later."
                }
            )

        # Log the current valid transaction timestamp
        self.client_records[client_ip].append(current_time)
        return await call_next(request)
    