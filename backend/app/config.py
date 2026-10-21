"""
Application Configuration
Loads settings from environment variables or .env file with sensible defaults.
"""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = (BACKEND_DIR / "campus_connect.db").as_posix()
DEFAULT_UPLOAD_DIR = (BACKEND_DIR / "uploads" / "resumes").as_posix()


class Settings(BaseSettings):
    APP_NAME: str = "Internship and Placement Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"

    # JWT Authentication
    SECRET_KEY: str = "campus_connect_secure_jwt_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Resume File Uploads
    UPLOAD_DIR: str = DEFAULT_UPLOAD_DIR
    MAX_RESUME_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB

    # Controlled Initial Admin Setup
    INITIAL_ADMIN_EMAIL: str = "admin@campusconnect.edu"
    INITIAL_ADMIN_PASSWORD: str = "Admin@123"
    INITIAL_ADMIN_NAME: str = "Placement Administrator"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
