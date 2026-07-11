# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Road Damage API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str

    # New Security Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Used to build absolute URLs for uploaded images (e.g. "<BACKEND_BASE_URL>/static/<file>")
    BACKEND_BASE_URL: str = "http://localhost:8000"

    # Used in emails (e.g. "Open <FRONTEND_URL>/login") and CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Email / OTP settings (Gmail SMTP) ---
    # Gmail requires an "App Password" (Google Account -> Security -> 2-Step
    # Verification -> App Passwords), NOT your normal Gmail login password.
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""          # e.g. yourapp@gmail.com
    SMTP_PASSWORD: str = ""      # 16-character Gmail App Password
    SMTP_FROM_EMAIL: str = ""    # defaults to SMTP_USER if left blank
    SMTP_FROM_NAME: str = "Road Damage AI"

    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 20

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()