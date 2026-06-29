# app/middleware/logging.py
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Intercepts inbound HTTP transfers, timing processing speed and logging details."""
        start_time = time.time()
        
        # Capture raw request context metrics
        method = request.method
        url = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Pass request downstream to the targeted endpoint router
        response = await call_next(request)
        
        # Calculate overall runtime latency
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = f"{process_time:.2f}ms"
        
        # Log HTTP transaction metrics
        logger.info(
            f"Client: {client_host} | HTTP {method} {url} | Status: {response.status_code} | Latency: {formatted_process_time}"
        )
        
        # Append performance timing telemetry header directly to the response metadata
        response.headers["X-Process-Time"] = formatted_process_time
        return response