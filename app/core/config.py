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

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()