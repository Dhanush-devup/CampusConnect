"""
Alembic migration tests.
Verifies that migrations build the same schema as the models, and that databases
created before Alembic existed are upgraded in place without losing rows.
"""
import sqlite3

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
import pytest
from sqlalchemy import create_engine, inspect

from app.database import Base, upgrade_db

# Schema produced by an older version of the models (before Alembic): no 'pending'
# account status, and ON DELETE CASCADE where the models now use RESTRICT.
LEGACY_SCHEMA = """
CREATE TABLE companies (
    company_id INTEGER NOT NULL, company_name VARCHAR(150) NOT NULL, email VARCHAR(255) NOT NULL,
    phone VARCHAR(30), industry VARCHAR(100), location VARCHAR(150), website VARCHAR(255),
    PRIMARY KEY (company_id)
);
CREATE INDEX ix_companies_company_id ON companies (company_id);
CREATE TABLE users (
    user_id INTEGER NOT NULL, name VARCHAR(100) NOT NULL, email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL, role VARCHAR(20) NOT NULL, account_status VARCHAR(20) NOT NULL,
    company_id INTEGER, created_at DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    CONSTRAINT check_user_role CHECK (role IN ('student', 'recruiter', 'admin')),
    CONSTRAINT check_user_account_status CHECK (account_status IN ('active', 'disabled')),
    FOREIGN KEY(company_id) REFERENCES companies (company_id) ON DELETE SET NULL
);
CREATE INDEX ix_users_user_id ON users (user_id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE TABLE opportunities (
    opportunity_id INTEGER NOT NULL, company_id INTEGER NOT NULL, title VARCHAR(150) NOT NULL,
    opportunity_type VARCHAR(20) NOT NULL, description TEXT NOT NULL, location VARCHAR(150),
    salary_stipend FLOAT, deadline DATETIME NOT NULL, eligibility_cgpa FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL, created_at DATETIME NOT NULL,
    PRIMARY KEY (opportunity_id),
    FOREIGN KEY(company_id) REFERENCES companies (company_id) ON DELETE CASCADE
);
CREATE INDEX ix_opportunities_opportunity_id ON opportunities (opportunity_id);
CREATE TABLE students (
    student_id INTEGER NOT NULL, user_id INTEGER NOT NULL, department VARCHAR(100) NOT NULL,
    cgpa FLOAT NOT NULL, graduation_year INTEGER NOT NULL,
    PRIMARY KEY (student_id), UNIQUE (user_id),
    FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
CREATE INDEX ix_students_student_id ON students (student_id);
CREATE TABLE applications (
    application_id INTEGER NOT NULL, student_id INTEGER NOT NULL, opportunity_id INTEGER NOT NULL,
    application_date DATETIME NOT NULL, status VARCHAR(20) NOT NULL, resume_path VARCHAR(500),
    PRIMARY KEY (application_id),
    CONSTRAINT uq_student_opportunity_application UNIQUE (student_id, opportunity_id),
    FOREIGN KEY(student_id) REFERENCES students (student_id) ON DELETE CASCADE,
    FOREIGN KEY(opportunity_id) REFERENCES opportunities (opportunity_id) ON DELETE CASCADE
);
CREATE INDEX ix_applications_application_id ON applications (application_id);

INSERT INTO companies VALUES (1, 'Acme', 'hr@acme.com', NULL, NULL, NULL, NULL);
INSERT INTO users VALUES (1, 'Rita', 'rita@acme.com', 'x', 'recruiter', 'active', 1, '2026-01-01');
INSERT INTO users VALUES (2, 'Sam', 'sam@college.edu', 'x', 'student', 'active', NULL, '2026-01-01');
INSERT INTO students VALUES (1, 2, 'CSE', 8.5, 2026);
INSERT INTO opportunities VALUES (1, 1, 'Intern', 'internship', 'Build things', NULL, NULL,
    '2027-01-01', 7.0, 'open', '2026-01-01');
INSERT INTO applications VALUES (1, 1, 1, '2026-02-01', 'applied', NULL);
"""

TABLES = ["users", "students", "companies", "opportunities", "applications"]


def sqlite_url(path):
    return f"sqlite:///{path.as_posix()}"


def row_counts(path):
    with sqlite3.connect(path) as conn:
        return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}


def ondelete_rules(path, table):
    with sqlite3.connect(path) as conn:
        return {row[3]: row[6] for row in conn.execute(f"PRAGMA foreign_key_list({table})")}


def schema_drift(path):
    """Differences between app.models and the database schema (empty when in sync)."""
    engine = create_engine(sqlite_url(path))
    try:
        with engine.connect() as conn:
            return compare_metadata(MigrationContext.configure(conn), Base.metadata)
    finally:
        engine.dispose()


def test_migrations_create_full_schema_on_empty_database(tmp_path):
    db_path = tmp_path / "fresh.db"
    upgrade_db(sqlite_url(db_path))

    engine = create_engine(sqlite_url(db_path))
    try:
        assert set(TABLES) <= set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "0003"
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role, account_status, created_at) "
            "VALUES ('P', 'p@x.com', 'x', 'recruiter', 'pending', '2026-01-01')"
        )
    assert ondelete_rules(db_path, "applications") == {"student_id": "RESTRICT", "opportunity_id": "RESTRICT"}
    assert schema_drift(db_path) == []


def test_legacy_database_is_upgraded_without_losing_rows(tmp_path):
    db_path = tmp_path / "legacy.db"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(LEGACY_SCHEMA)
    before = row_counts(db_path)

    upgrade_db(sqlite_url(db_path))

    # No rows lost (rebuilding 'users' with foreign keys on would cascade into students)
    assert row_counts(db_path) == before

    # Old CASCADE rules replaced by RESTRICT, matching app.models
    assert ondelete_rules(db_path, "opportunities") == {"company_id": "RESTRICT"}
    assert ondelete_rules(db_path, "applications") == {"student_id": "RESTRICT", "opportunity_id": "RESTRICT"}

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        # 'pending' is now accepted, unknown statuses still rejected
        conn.execute("UPDATE users SET account_status = 'pending' WHERE user_id = 1")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE users SET account_status = 'banned' WHERE user_id = 1")
        # Deleting a company with opportunities is now blocked instead of cascading
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM companies WHERE company_id = 1")
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        # Unique email index survives the table rebuild
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO users (name, email, password_hash, role, account_status, created_at) "
                "VALUES ('Dup', 'rita@acme.com', 'x', 'admin', 'active', '2026-01-01')"
            )
    assert schema_drift(db_path) == []

    # Running again is a no-op
    upgrade_db(sqlite_url(db_path))
    assert row_counts(db_path) == before
