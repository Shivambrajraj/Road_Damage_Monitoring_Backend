import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import uvicorn

from app.core.database import engine, Base, SessionLocal
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.api.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.authentication import GlobalAuthMiddleware
from app.middleware.authorization import MaintenanceLockMiddleware
from app.exceptions.custom import AppException, database_integrity_exception_handler

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
    with engine.begin() as conn:  # engine.begin() automatically handles transaction commit
        conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS reported_by_id INTEGER REFERENCES users(id);"))
    logger.info("Successfully checked/added missing reported_by_id column to database.")
except Exception as e:
    logger.warning(f"Database column fix skipped or already applied: {e}")

# --- Helper to ensure columns exist (works for both Postgres and SQLite) ---
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

# --- New columns execution block for the reports status tracking schema ---
try:
    with engine.begin() as conn:
        _ensure_column(conn, "reports", "status", "VARCHAR DEFAULT 'pending'")
        _ensure_column(conn, "reports", "status_updated_at", "TIMESTAMP")
    logger.info("Successfully checked/added missing status columns to reports.")
except Exception as e:
    logger.warning(f"reports.status column fix skipped or already applied: {e}")
# -----------------------------------------------

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
except Exception as e:
    logger.error(f"CRITICAL: Could not connect to the database at startup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Modern lifespan handler replacing deprecated on_event("startup")
    try:
        print("Executing Admin Promotion Script...")
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "create_admin.py"
        subprocess.run([sys.executable, str(script_path)], check=True)
        print("Admin Promotion Completed Successfully!")
    except Exception as e:
        print(f"Admin Promotion script failed on startup: {str(e)}")
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

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

app.add_exception_handler(IntegrityError, database_integrity_exception_handler)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError",
            "detail": "Something went wrong on our end. Please try again shortly.",
        },
    )

# Ensure required upload directories exist on startup
STORAGE_PATHS = [
    "app/storage/uploads",
    "app/storage/uploads/original",
    "app/storage/uploads/processed",
    "app/storage/uploads/thumbnails",
    "app/storage/exports"
]

for path in STORAGE_PATHS:
    os.makedirs(path, exist_ok=True)

# Static file mounts to serve both uploaded raw photos and YOLO segmentation output images
app.mount("/static/original", StaticFiles(directory="app/storage/uploads/original"), name="static_original")
app.mount("/static/processed", StaticFiles(directory="app/storage/uploads/processed"), name="static_processed")
app.mount("/static", StaticFiles(directory="app/storage/uploads"), name="static_uploads")

# --- Production Health Check Endpoint ---
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
        logger.error(f"Health Check Failure: {str(e)}")
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