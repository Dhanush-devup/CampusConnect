"""
Pytest configuration and shared fixtures for Phase 1 testing.
Uses an isolated temporary SQLite database for test execution.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
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
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
