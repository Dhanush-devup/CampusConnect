"""
Pytest configuration and shared fixtures for Phase 1 testing.
Uses an isolated temporary SQLite database for test execution.
"""
import os
from pathlib import Path
import tempfile

# Point the app at throwaway locations before any app module reads settings,
# so the app's startup (migrations, admin seeding, resume uploads) never touches
# the real database or uploads folder.
_TEST_DIR = Path(tempfile.mkdtemp(prefix="campusconnect_tests_"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TEST_DIR / 'app.db').as_posix()}"
os.environ["UPLOAD_DIR"] = (_TEST_DIR / "resumes").as_posix()
# Never call the real Gemini API from tests, even if backend/.env has a key
os.environ["GEMINI_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, get_session_factory
from app.main import app


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Provides a path to an isolated temporary SQLite database."""
    temp_dir = tmp_path_factory.mktemp("test_db")
    db_file = temp_dir / "test_campus_connect.db"
    return str(db_file)


@pytest.fixture(scope="session")
def test_engine(test_db_path):
    """
    Creates a dedicated SQLAlchemy engine for testing.
    SQLite foreign key pragma is automatically enforced via Engine event listener.
    """
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    # Initialize all five tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass


@pytest.fixture
def db_session(test_engine):
    """
    Provides a clean transactional session for each test function.
    Rolls back any uncommitted state upon completion.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def clean_database(test_engine):
    """
    Cleans data from all tables between tests to maintain test isolation.
    """
    yield
    with test_engine.connect() as conn:
        # Delete rows in reverse-dependency order
        conn.execute(text("DELETE FROM resume_scores;"))
        conn.execute(text("DELETE FROM applications;"))
        conn.execute(text("DELETE FROM opportunities;"))
        conn.execute(text("DELETE FROM students;"))
        conn.execute(text("DELETE FROM users;"))
        conn.execute(text("DELETE FROM companies;"))
        conn.commit()


@pytest.fixture
def client(test_engine, db_session):
    """
    FastAPI TestClient with overridden get_db dependency pointing to the test database.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # Background tasks (ATS scoring) open their own sessions on the test database
    app.dependency_overrides[get_session_factory] = lambda: sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
