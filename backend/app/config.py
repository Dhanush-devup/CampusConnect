"""
Application Configuration
Loads settings from environment variables or .env file with sensible defaults.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = (BACKEND_DIR / "campus_connect.db").as_posix()
DEFAULT_UPLOAD_DIR = (BACKEND_DIR / "uploads" / "resumes").as_posix()

# Development-only defaults. The app refuses to start outside development
# while any of these are still in use.
DEV_SECRET_KEY = "campus_connect_secure_jwt_secret_key_change_in_production"
DEV_ADMIN_PASSWORD = "Admin@123"


class Settings(BaseSettings):
    APP_NAME: str = "Internship and Placement Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"

    # JWT Authentication
    SECRET_KEY: str = DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Resume File Uploads
    UPLOAD_DIR: str = DEFAULT_UPLOAD_DIR
    MAX_RESUME_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB

    # Controlled Initial Admin Setup
    INITIAL_ADMIN_EMAIL: str = "admin@campusconnect.edu"
    INITIAL_ADMIN_PASSWORD: str = DEV_ADMIN_PASSWORD
    INITIAL_ADMIN_NAME: str = "Placement Administrator"

    # ATS resume scoring. Without a key, resumes get the rule-based score only.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    # Tried in order when the main model is overloaded (JSON list in .env)
    GEMINI_FALLBACK_MODELS: List[str] = ["gemini-3.5-flash-lite"]
    GEMINI_TIMEOUT_SECONDS: float = 45.0

    # Browser origins allowed to call the API (JSON list in .env)
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def reject_dev_secrets_outside_development(self) -> "Settings":
        if self.ENVIRONMENT != "development":
            if self.SECRET_KEY == DEV_SECRET_KEY:
                raise ValueError("SECRET_KEY must be set in .env outside development.")
            if self.INITIAL_ADMIN_PASSWORD == DEV_ADMIN_PASSWORD:
                raise ValueError("INITIAL_ADMIN_PASSWORD must be set in .env outside development.")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS must not contain '*' outside development.")
        return self


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
