"""
Phase 1 Test Suite for CampusConnect.
Verifies:
- Application startup and /health response
- Creation and existence of all 5 tables (users, students, companies, opportunities, applications)
- Active SQLite foreign key pragma enforcement
- CGPA check constraints (0.0 to 10.0) on students and opportunities
- Salary stipend non-negative constraint
- Unique constraint preventing duplicate student applications
- Foreign key constraint enforcement across entities
- Model relationships and cascading behaviors
"""
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from fastapi import status

from app.models import Application, Company, Opportunity, Student, User


def create_user(session, email="alice@college.edu", role="student", name="Alice Smith", **kwargs):
    user = User(
        name=name,
        email=email,
        password_hash="mock_hashed_secret",
        role=role,
        account_status="active",
        **kwargs,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_company(session, name="TechCorp Solutions", email="hr@techcorp.com", **kwargs):
    company = Company(
        company_name=name,
        email=email,
        phone="+1234567890",
        industry="Software",
        location="Bangalore",
        website="https://techcorp.com",
        **kwargs,
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def create_student(session, user_id, department="Computer Science", cgpa=8.5, graduation_year=2026):
    student = Student(
        user_id=user_id,
        department=department,
        cgpa=cgpa,
        graduation_year=graduation_year,
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def create_opportunity(session, company_id, title="Software Engineering Intern", eligibility_cgpa=7.0, **kwargs):
    deadline = datetime.now(timezone.utc) + timedelta(days=30)
    opportunity = Opportunity(
        company_id=company_id,
        title=title,
        opportunity_type="internship",
        description="Exciting internship opportunity for engineering students.",
        location="Remote",
        salary_stipend=35000.0,
        deadline=deadline,
        eligibility_cgpa=eligibility_cgpa,
        status="open",
        **kwargs,
    )
    session.add(opportunity)
    session.commit()
    session.refresh(opportunity)
    return opportunity


# ============================================================================
# 1. Application Startup & Health Check Tests
# ============================================================================

def test_app_starts_and_root_endpoint_returns_ok(client):
    """Test that the application starts and the root endpoint returns 200."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "docs_url" in data
    assert "health_url" in data


def test_health_check_returns_healthy(client):
    """Test GET /health returns 200 with healthy status and database connected."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "app_name" in data
    assert "environment" in data


# ============================================================================
# 2. Database Schema & Five Tables Verification
# ============================================================================

def test_database_has_exactly_five_application_tables(test_engine):
    """Verify that all five required application tables exist in the database."""
    inspector = inspect(test_engine)
    table_names = set(inspector.get_table_names())
    expected_tables = {
        "users",
        "students",
        "companies",
        "opportunities",
        "applications",
        "resume_scores",
    }
    assert expected_tables.issubset(table_names), f"Missing tables: {expected_tables - table_names}"


# ============================================================================
# 3. SQLite Foreign Key Enforcement Check
# ============================================================================

def test_sqlite_foreign_keys_pragma_is_active(db_session):
    """Verify that PRAGMA foreign_keys is enabled (1) on SQLite connections."""
    result = db_session.execute(text("PRAGMA foreign_keys;")).scalar()
    assert result == 1, "Foreign key enforcement is not enabled on SQLite connection!"


# ============================================================================
# 4. CGPA Check Constraint Tests
# ============================================================================

def test_student_cgpa_constraint_rejects_negative_value(db_session):
    """Check constraint must reject CGPA < 0."""
    user = create_user(db_session, email="cgpa_neg@college.edu")
    invalid_student = Student(
        user_id=user.user_id,
        department="Information Technology",
        cgpa=-0.5,
        graduation_year=2026,
    )
    db_session.add(invalid_student)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_student_cgpa_constraint_rejects_value_above_ten(db_session):
    """Check constraint must reject CGPA > 10.0."""
    user = create_user(db_session, email="cgpa_over@college.edu")
    invalid_student = Student(
        user_id=user.user_id,
        department="Information Technology",
        cgpa=10.5,
        graduation_year=2026,
    )
    db_session.add(invalid_student)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_student_cgpa_boundary_values_accepted(db_session):
    """Valid boundary values (0.0 and 10.0) should be accepted."""
    user1 = create_user(db_session, email="bound0@college.edu")
    user2 = create_user(db_session, email="bound10@college.edu")

    student1 = create_student(db_session, user_id=user1.user_id, cgpa=0.0)
    student2 = create_student(db_session, user_id=user2.user_id, cgpa=10.0)

    assert student1.cgpa == 0.0
    assert student2.cgpa == 10.0


def test_opportunity_eligibility_cgpa_constraint(db_session):
    """Opportunity eligibility_cgpa must reject values outside 0-10 range."""
    company = create_company(db_session, email="cgpa_opp@company.com")
    deadline = datetime.now(timezone.utc) + timedelta(days=15)

    invalid_opp = Opportunity(
        company_id=company.company_id,
        title="Software Engineer",
        opportunity_type="full_time",
        description="Great role",
        deadline=deadline,
        eligibility_cgpa=11.0,
        status="open",
    )
    db_session.add(invalid_opp)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_opportunity_salary_stipend_cannot_be_negative(db_session):
    """Opportunity salary_stipend must reject negative numbers."""
    company = create_company(db_session, email="salary_opp@company.com")
    deadline = datetime.now(timezone.utc) + timedelta(days=15)

    invalid_opp = Opportunity(
        company_id=company.company_id,
        title="Marketing Intern",
        opportunity_type="internship",
        description="Marketing role",
        salary_stipend=-500.0,
        deadline=deadline,
        eligibility_cgpa=6.5,
        status="open",
    )
    db_session.add(invalid_opp)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ============================================================================
# 5. Duplicate Application Check (Unique Constraint)
# ============================================================================

def test_duplicate_student_applications_rejected(db_session):
    """
    Ensure the UNIQUE constraint (student_id, opportunity_id) prevents
    a student from applying to the same opportunity more than once.
    """
    user = create_user(db_session, email="applicant@college.edu")
    student = create_student(db_session, user_id=user.user_id)
    company = create_company(db_session, email="recruiting@dups.com")
    opportunity = create_opportunity(db_session, company_id=company.company_id)

    # First application succeeds
    app1 = Application(
        student_id=student.student_id,
        opportunity_id=opportunity.opportunity_id,
        status="applied",
    )
    db_session.add(app1)
    db_session.commit()

    # Second application for same student and same opportunity must fail
    app2 = Application(
        student_id=student.student_id,
        opportunity_id=opportunity.opportunity_id,
        status="applied",
    )
    db_session.add(app2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ============================================================================
# 6. Foreign Key Enforcement Tests
# ============================================================================

def test_foreign_key_violation_student_without_user(db_session):
    """Inserting a student profile referencing a non-existent user_id must fail."""
    orphan_student = Student(
        user_id=999999,  # Non-existent user
        department="Mechanical",
        cgpa=8.0,
        graduation_year=2026,
    )
    db_session.add(orphan_student)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_foreign_key_violation_opportunity_without_company(db_session):
    """Inserting an opportunity referencing a non-existent company_id must fail."""
    deadline = datetime.now(timezone.utc) + timedelta(days=10)
    orphan_opp = Opportunity(
        company_id=999999,  # Non-existent company
        title="Product Designer",
        opportunity_type="full_time",
        description="Design apps",
        deadline=deadline,
        eligibility_cgpa=7.0,
        status="open",
    )
    db_session.add(orphan_opp)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_foreign_key_violation_application_without_student_or_opportunity(db_session):
    """Inserting an application referencing non-existent student or opportunity must fail."""
    orphan_app = Application(
        student_id=999999,
        opportunity_id=999999,
        status="applied",
    )
    db_session.add(orphan_app)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ============================================================================
# 7. Additional Schema Constraints Tests (Roles, Statuses, Unique Email)
# ============================================================================

def test_user_email_must_be_unique(db_session):
    """Users cannot share the same email address."""
    create_user(db_session, email="unique@college.edu")
    duplicate_user = User(
        name="Bob Duplicate",
        email="unique@college.edu",
        password_hash="hashed_secret",
        role="student",
        account_status="active",
    )
    db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_role_check_constraint(db_session):
    """Invalid user roles must be rejected."""
    invalid_user = User(
        name="Hacker",
        email="hacker@test.com",
        password_hash="hashed_secret",
        role="superuser",  # Not in ('student', 'recruiter', 'admin')
        account_status="active",
    )
    db_session.add(invalid_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_student_profile_must_be_one_to_one(db_session):
    """A user cannot have multiple student profiles (user_id is UNIQUE)."""
    user = create_user(db_session, email="onetoone@college.edu")
    create_student(db_session, user_id=user.user_id)

    # Attempting to create a second student profile for the same user must fail
    second_student = Student(
        user_id=user.user_id,
        department="Electrical",
        cgpa=9.1,
        graduation_year=2026,
    )
    db_session.add(second_student)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ============================================================================
# 8. Model Relationships Navigation Test
# ============================================================================

def test_model_relationships_navigation(db_session):
    """
    Verify bidirectional SQLAlchemy relationships:
    - User <-> Student (1:1)
    - Company <-> Recruiters (1:N)
    - Company <-> Opportunities (1:N)
    - Student <-> Applications (1:N)
    - Opportunity <-> Applications (1:N)
    """
    # 1. Company with Recruiter
    company = create_company(db_session, name="Global Innovations", email="contact@global.com")
    recruiter = create_user(
        db_session,
        email="recruiter@global.com",
        role="recruiter",
        company_id=company.company_id,
    )

    # Check recruiter <-> company relationship
    assert recruiter.company is not None
    assert recruiter.company.company_name == "Global Innovations"
    assert recruiter in company.recruiters

    # 2. Student user and profile
    student_user = create_user(db_session, email="john.doe@college.edu", role="student", name="John Doe")
    student = create_student(db_session, user_id=student_user.user_id, department="CSE", cgpa=8.8)

    # Check student <-> user relationship
    assert student_user.student_profile is not None
    assert student_user.student_profile.department == "CSE"
    assert student.user.email == "john.doe@college.edu"

    # 3. Opportunity under company
    opp = create_opportunity(db_session, company_id=company.company_id, title="Backend Developer Intern")
    assert opp in company.opportunities
    assert opp.company.company_name == "Global Innovations"

    # 4. Application connecting student and opportunity
    app = Application(
        student_id=student.student_id,
        opportunity_id=opp.opportunity_id,
        status="applied",
        resume_path="/resumes/john_doe_resume.pdf",
    )
    db_session.add(app)
    db_session.commit()
    db_session.refresh(app)

    # Check application relationships
    assert app.student.student_id == student.student_id
    assert app.opportunity.opportunity_id == opp.opportunity_id
    assert app in student.applications
    assert app in opp.applications


# ============================================================================
# 9. Application History Protection (ON DELETE RESTRICT Tests)
# ============================================================================

def test_delete_student_with_existing_applications_is_rejected(db_session):
    """
    Deleting a student who has submitted applications must be rejected
    to protect placement history and audit records.
    """
    user = create_user(db_session, email="protect_student@college.edu")
    student = create_student(db_session, user_id=user.user_id)
    company = create_company(db_session, email="audit_co@test.com")
    opp = create_opportunity(db_session, company_id=company.company_id)

    app = Application(
        student_id=student.student_id,
        opportunity_id=opp.opportunity_id,
        status="applied",
    )
    db_session.add(app)
    db_session.commit()

    # Attempting to delete the student must raise IntegrityError
    db_session.delete(student)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_delete_opportunity_with_existing_applications_is_rejected(db_session):
    """
    Deleting an opportunity with existing student applications must be rejected.
    Opportunities should be marked as 'closed' rather than deleted.
    """
    user = create_user(db_session, email="protect_opp_student@college.edu")
    student = create_student(db_session, user_id=user.user_id)
    company = create_company(db_session, email="audit_opp_co@test.com")
    opp = create_opportunity(db_session, company_id=company.company_id)

    app = Application(
        student_id=student.student_id,
        opportunity_id=opp.opportunity_id,
        status="applied",
    )
    db_session.add(app)
    db_session.commit()

    # Attempting to delete the opportunity must raise IntegrityError
    db_session.delete(opp)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_delete_company_with_opportunities_is_rejected(db_session):
    """
    Deleting a company that has posted opportunities must be rejected.
    This prevents indirect cascade deletion of opportunities and student applications.
    """
    user = create_user(db_session, email="company_protect_stud@college.edu")
    student = create_student(db_session, user_id=user.user_id)
    company = create_company(db_session, email="audit_parent_co@test.com")
    opp = create_opportunity(db_session, company_id=company.company_id)

    app = Application(
        student_id=student.student_id,
        opportunity_id=opp.opportunity_id,
        status="applied",
    )
    db_session.add(app)
    db_session.commit()

    # Attempting to delete the company must raise IntegrityError
    db_session.delete(company)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_raw_sql_delete_restricted_by_database_engine(db_session):
    """
    Direct SQL DELETE statements must also be blocked by the SQLite database engine
    itself, proving that protection is not just ORM-dependent.
    """
    user = create_user(db_session, email="raw_sql_stud@college.edu")
    student = create_student(db_session, user_id=user.user_id)
    company = create_company(db_session, email="raw_sql_co@test.com")
    opp = create_opportunity(db_session, company_id=company.company_id)

    app = Application(
        student_id=student.student_id,
        opportunity_id=opp.opportunity_id,
        status="applied",
    )
    db_session.add(app)
    db_session.commit()

    # 1. Direct SQL delete of student
    with pytest.raises(IntegrityError):
        db_session.execute(text(f"DELETE FROM students WHERE student_id = {student.student_id};"))
        db_session.commit()
    db_session.rollback()

    # 2. Direct SQL delete of opportunity
    with pytest.raises(IntegrityError):
        db_session.execute(text(f"DELETE FROM opportunities WHERE opportunity_id = {opp.opportunity_id};"))
        db_session.commit()
    db_session.rollback()

    # 3. Direct SQL delete of company
    with pytest.raises(IntegrityError):
        db_session.execute(text(f"DELETE FROM companies WHERE company_id = {company.company_id};"))
        db_session.commit()
    db_session.rollback()


