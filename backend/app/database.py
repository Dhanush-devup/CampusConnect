"""
Database configuration and session management.
Ensures SQLite foreign keys are enforced on every database connection.
"""
from typing import Generator
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import BACKEND_DIR, get_settings

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


def get_session_factory() -> sessionmaker:
    """
    FastAPI dependency for work that outlives the request (background tasks),
    which must open its own session. Overridden in tests.
    """
    return SessionLocal


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


# Revision that matches the schema created before Alembic was introduced
BASELINE_REVISION = "0001"


def upgrade_db(database_url: str | None = None) -> None:
    """
    Brings the database schema up to date by running Alembic migrations.
    Databases created before migrations existed (tables present, no alembic_version)
    are stamped at the baseline revision first, then upgraded.
    """
    from alembic import command
    from alembic.config import Config

    url = database_url or settings.DATABASE_URL
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["configure_logger"] = False
    config.attributes["database_url"] = url

    check_engine = create_engine(url)
    try:
        tables = inspect(check_engine).get_table_names()
    finally:
        check_engine.dispose()

    if "users" in tables and "alembic_version" not in tables:
        command.stamp(config, BASELINE_REVISION)
    command.upgrade(config, "head")
