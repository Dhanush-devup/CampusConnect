"""
FastAPI Application Entry Point.
Initializes the database, exposes system endpoints, configures CORS,
and registers all API route modules for CampusConnect.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import get_settings
from app.database import SessionLocal, get_db, init_db
from app.models import User
from app.routers import admin, applications, auth, opportunities, profiles
from app.schemas import HealthCheckResponse

settings = get_settings()


def ensure_initial_admin():
    """Provisions a default administrator if no admin account exists."""
    session = SessionLocal()
    try:
        admin_user = session.query(User).filter(User.role == "admin").first()
        if not admin_user:
            initial_admin = User(
                name=settings.INITIAL_ADMIN_NAME,
                email=settings.INITIAL_ADMIN_EMAIL.lower().strip(),
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role="admin",
                account_status="active",
                company_id=None,
            )
            session.add(initial_admin)
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database tables, creates upload directories, and seeds initial admin.
    """
    init_db()
    # Ensure uploads directory exists
    Path(settings.UPLOAD_DIR).resolve().mkdir(parents=True, exist_ok=True)
    # Seed initial admin if necessary
    ensure_initial_admin()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend API for the College Internship and Placement Management System. "
        "Complete REST APIs for Authentication, Student Portals, Recruiter Management, "
        "and Institutional Administration."
    ),
    lifespan=lifespan,
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router)
app.include_router(opportunities.router)
app.include_router(applications.router)
app.include_router(profiles.router)
app.include_router(admin.router)


@app.get(
    "/",
    tags=["Root"],
    summary="Root Welcome Endpoint",
)
def root():
    """Welcome endpoint pointing to API documentation."""
    return {
        "message": f"Welcome to the {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="System Health and Database Connectivity Check",
)
@app.get(
    "/api/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="System Health and Database Connectivity Check (API prefix)",
)
def health_check(db: Session = Depends(get_db)):
    """
    Verifies the operational status of the service and confirms
    active connectivity with the SQLite database.
    """
    try:
        # Run a simple probe query to verify database connectivity
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(exc)}",
        )

    return HealthCheckResponse(
        status="healthy",
        database=db_status,
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
    )
