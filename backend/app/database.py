"""
Database configuration and session management.
Ensures SQLite foreign keys are enforced on every database connection.
"""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings

settings = get_settings()


# Enable SQLite foreign key support on EVERY connection
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Ensure SQLite enforces foreign key constraints.
    By default in SQLite, foreign key enforcement is disabled.
    """
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Connection arguments for SQLite (allows usage across FastAPI async threads)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Rolls back automatically on unhandled exceptions and guarantees session closure.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db(target_engine=None) -> None:
    """
    Creates all database tables defined in SQLAlchemy models.
    """
    active_engine = target_engine or engine
    Base.metadata.create_all(bind=active_engine)
