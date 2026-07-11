# app/api/router.py
from fastapi import APIRouter

# Import all sub-routers explicitly
from app.api.v1.reports import router as reports_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.maps import router as maps_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

# Register each sub-router into the main API tree
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(maps_router, prefix="/maps", tags=["Maps"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])