# app/schemas/auth.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    verification_token: str  # issued by POST /auth/verify-otp after the email OTP challenge

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: bool