# Internship and Placement Management System — Backend

Phase 1 foundation: Clean SQLite database schema with SQLAlchemy ORM, Pydantic validation, and FastAPI backend foundation.

---

## Folder Structure

```text
backend/
├── app/
│   ├── __init__.py      # Package indicator
│   ├── config.py        # Environment variables and application configuration
│   ├── database.py      # SQLAlchemy engine, session maker, get_db dependency, and SQLite FK pragma
│   ├── models.py        # 5 Core SQLAlchemy tables with constraints and relationships
│   ├── schemas.py       # Pydantic validation schemas for data input/output
│   ├── main.py          # FastAPI application entry point, lifespan, and /health check
│   ├── auth.py          # Password hashing, JWT tokens, role-based dependencies
│   └── routers/         # API endpoints: auth, opportunities, applications, profiles, admin
├── migrations/          # Alembic database migrations (versions/ holds each schema change)
├── alembic.ini          # Alembic configuration
├── tests/
│   ├── __init__.py      # Test package indicator
│   ├── conftest.py      # Pytest fixtures and temporary isolated SQLite test database
│   ├── test_api.py      # API, permission, and business-rule tests
│   ├── test_database.py # Automated tests for constraints, foreign keys, tables, and endpoints
│   └── test_migrations.py # Migrations build the model schema and upgrade old databases safely
├── .env.example         # Template for environment configuration
├── requirements.txt     # Python backend dependencies
└── README.md            # Backend documentation and instructions
```

---

## Quick Setup Instructions

### 1. Navigate to the backend folder
```bash
cd backend
```

### 2. Create and activate a virtual environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)
```powershell
Copy-Item .env.example .env
```

### 5. Run automated tests
```bash
pytest -v tests
```

### 6. Run the FastAPI development server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Database Migrations (Alembic)

The schema is managed with Alembic. **The app applies pending migrations automatically on startup**, so a normal `uvicorn` start keeps the database up to date. Databases created before Alembic was added are detected and upgraded in place.

When you change `app/models.py`, create a migration and review it before committing:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
alembic check   # confirms models and database match
```

SQLite cannot alter constraints in place, so migrations use Alembic batch mode (the table is rebuilt and rows copied). Foreign keys are switched off during migrations so rebuilding a parent table never cascades deletes into child tables.

---

## Production Settings

Outside `ENVIRONMENT=development` the app refuses to start unless `SECRET_KEY` and `INITIAL_ADMIN_PASSWORD` are changed from their defaults, and `CORS_ORIGINS` must not contain `*`. See `.env.example`.
