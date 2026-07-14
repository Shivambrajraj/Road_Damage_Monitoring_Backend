# app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app.core.database import engine, Base, SessionLocal

from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.api.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.authentication import GlobalAuthMiddleware
from app.middleware.authorization import MaintenanceLockMiddleware
# Updated Import Path to reflect consolidated exception domain:
from app.exceptions.custom import AppException, database_integrity_exception_handler

import subprocess
import sys
from pathlib import Path

import app.models.report 
import app.models.damage 
import app.models.user
import app.models.notification
import app.models.audit_log
import app.models.otp

configure_logging()
logger.info("Initializing Road Damage Monitoring platform services...")

# --- TEMPORARY RENDER FREE TIER DATABASE FIX ---
try:
    with engine.begin() as conn:  # engine.begin() automatically handles the transaction commit
        conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS reported_by_id INTEGER REFERENCES users(id);"))
    logger.info("Successfully checked/added missing reported_by_id column to database.")
except Exception as e:
    logger.warning(f"Database column fix skipped or already applied: {e}")

# --- Add is_verified to users (works for both Postgres and SQLite) ---
def _ensure_column(conn, table: str, column: str, ddl_type: str):
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    if is_sqlite:
        existing = [row[1] for row in conn.execute(text(f"PRAGMA table_info({table});"))]
        if column not in existing:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type};"))
    else:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {ddl_type};"))

try:
    with engine.begin() as conn:
        _ensure_column(conn, "users", "is_verified", "BOOLEAN DEFAULT FALSE")
    logger.info("Successfully checked/added missing is_verified column to users.")
except Exception as e:
    logger.warning(f"is_verified column fix skipped or already applied: {e}")
# -----------------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def trigger_admin_creation():
    try:
        print("Executing Admin Promotion Script...")
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "create_admin.py"
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("Admin Promotion Completed Successfully!")
    except Exception as e:
        print(f"Admin Promotion script failed on startup: {str(e)}")
        
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

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Safety net for any exception that isn't an AppException/HTTPException
    (e.g. a bug, a third-party library error, an SMTP timeout, etc.).

    Without this, Starlette's default error handling happens OUTSIDE the
    CORS middleware layer, so the response is sent back with no CORS
    headers at all. The browser then blocks the response entirely and
    the frontend sees what looks like a network/CORS failure instead of
    the real 500 error. Registering a handler here keeps every response
    inside the CORS-wrapped part of the middleware stack.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError",
            "detail": "Something went wrong on our end. Please try again shortly.",
        },
    )

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