# app/api/v1/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.otp import SendOTPRequest, SendOTPResponse, VerifyOTPRequest, VerifyOTPResponse
from app.services.auth_service import auth_service
from app.services.otp_service import otp_service

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and generates a secure
    JWT Bearer token for accessing restricted operations.
    """
    return auth_service.authenticate_user(db, credentials)

@router.post("/send-otp", response_model=SendOTPResponse)
def send_otp(payload: SendOTPRequest, db: Session = Depends(get_db)):
    """
    Step 1 of registration: emails a 6-digit one-time code to the given
    address via Gmail SMTP. The code expires after OTP_EXPIRE_MINUTES.
    """
    return otp_service.send_registration_otp(db, payload.email)

@router.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Step 2 of registration: checks the code the user typed in. On success
    returns a short-lived verification_token that /auth/register requires,
    proving this email really was OTP-checked.
    """
    token = otp_service.verify_registration_otp(db, payload.email, payload.otp)
    return VerifyOTPResponse(
        verified=True,
        verification_token=token,
        message="Email verified successfully.",
    )

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Step 3 of registration: creates the account. Requires a valid
    verification_token obtained from /auth/verify-otp — registration is
    rejected if the email was never OTP-verified.
    """
    return auth_service.register_user(db, payload)