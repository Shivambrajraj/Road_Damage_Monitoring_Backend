# app/api/v1/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import auth_service

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and generates a secure 
    JWT Bearer token for accessing restricted operations.
    """
    return auth_service.authenticate_user(db, credentials)

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Creates a new municipal engineer account. Rejects duplicate
    usernames/emails with a 400 and a clear message.
    """
    return auth_service.register_user(db, payload)