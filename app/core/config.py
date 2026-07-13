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

    # --- Email / OTP settings (Brevo transactional email HTTP API) ---
    # Render's free tier blocks outbound SMTP ports (25/465/587), so emails
    # are sent via Brevo's REST API over HTTPS (port 443) instead, which
    # cannot be blocked without breaking the app's own web traffic.
    # Get BREVO_API_KEY from: Brevo dashboard -> SMTP & API -> API Keys.
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""   # must be a verified sender in Brevo
    BREVO_SENDER_NAME: str = "Road Damage AI"

    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 20

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()