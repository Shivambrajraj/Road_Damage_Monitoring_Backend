# app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app.core.database import engine, Base, SessionLocal

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal  # Added SessionLocal for health check
from app.core.logging import configure_logging, logger
from app.api.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.authentication import GlobalAuthMiddleware
from app.middleware.authorization import MaintenanceLockMiddleware
# Updated Import Path to reflect consolidated exception domain:
from app.exceptions.custom import AppException, database_integrity_exception_handler

import app.models.report 
import app.models.damage 
import app.models.user
import app.models.notification
import app.models.audit_log

configure_logging()
logger.info("Initializing Road Damage Monitoring platform services...")

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(RateLimitMiddleware, requests_per_minute=30)
app.add_middleware(RequestLoggingMiddleware)
setup_cors(app)
app.add_middleware(MaintenanceLockMiddleware, system_lock=False)
app.add_middleware(GlobalAuthMiddleware)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException Intercepted: {exc.__class__.__name__} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "detail": exc.detail
        }
    )

# Updated target registration reference
app.add_exception_handler(IntegrityError, database_integrity_exception_handler)

STORAGE_PATHS = [
    "app/storage/uploads/original",
    "app/storage/uploads/processed",
    "app/storage/uploads/thumbnails",
    "app/storage/exports"
]

for path in STORAGE_PATHS:
    os.makedirs(path, exist_ok=True)

app.mount("/static", StaticFiles(directory="app/storage/uploads/original"), name="static")

# --- IMPROVEMENT: Production Health Check Endpoint ---
@app.get("/health", tags=["Monitoring"])
def health_check():
    """System health check endpoint for cloud/deployment monitoring."""
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1")) 
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        # Crucial Security Patch: Log the raw diagnostic trace internally
        logger.error(f"Health Check Failure: {str(e)}")
        
        # Return a generic, safe payload to the public network
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }
    finally:
        if db:
            db.close()
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} backend!"}