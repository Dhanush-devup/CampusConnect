"""
SQLAlchemy database models for CampusConnect.
Defines the five core application tables:
1. users
2. students
3. companies
4. opportunities
5. applications
"""
from datetime import datetime, timezone
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    """Return the current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


class User(Base):
    """
    Table A: users
    Stores base credentials and role information for all system actors.
    Roles: 'student', 'recruiter', 'admin'
    Account statuses: 'active', 'disabled'
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    account_status = Column(String(20), nullable=False, default="active")
    company_id = Column(
        Integer,
        ForeignKey("companies.company_id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'recruiter', 'admin')",
            name="check_user_role",
        ),
        CheckConstraint(
            "account_status IN ('active', 'disabled')",
            name="check_user_account_status",
        ),
    )

    # Relationships
    student_profile = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    company = relationship(
        "Company",
        back_populates="recruiters",
    )

    def __repr__(self) -> str:
        return f"<User id={self.user_id} email={self.email} role={self.role}>"


class Student(Base):
    """
    Table B: students
    Stores academic and profile details for students.
    Linked 1:1 with users table.
    """
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    department = Column(String(100), nullable=False)
    cgpa = Column(Float, nullable=False)
    graduation_year = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "cgpa >= 0.0 AND cgpa <= 10.0",
            name="check_student_cgpa",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="student_profile")
    applications = relationship(
        "Application",
        back_populates="student",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Student id={self.student_id} user_id={self.user_id} dept={self.department}>"


class Company(Base):
    """
    Table C: companies
    Stores company contact and organization profiles.
    """
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    industry = Column(String(100), nullable=True)
    location = Column(String(150), nullable=True)
    website = Column(String(255), nullable=True)

    # Relationships
    recruiters = relationship(
        "User",
        back_populates="company",
    )
    opportunities = relationship(
        "Opportunity",
        back_populates="company",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Company id={self.company_id} name={self.company_name}>"


class Opportunity(Base):
    """
    Table D: opportunities
    Stores internship, full-time and part-time job postings by companies.
    Opportunity types: 'internship', 'full_time', 'part_time'
    Statuses: 'draft', 'open', 'closed'
    """
    __tablename__ = "opportunities"

    opportunity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.company_id", ondelete="RESTRICT"),
        nullable=False,
    )
    title = Column(String(150), nullable=False)
    opportunity_type = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(150), nullable=True)
    salary_stipend = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=False)
    eligibility_cgpa = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint(
            "opportunity_type IN ('internship', 'full_time', 'part_time')",
            name="check_opportunity_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'open', 'closed')",
            name="check_opportunity_status",
        ),
        CheckConstraint(
            "eligibility_cgpa >= 0.0 AND eligibility_cgpa <= 10.0",
            name="check_opportunity_eligibility_cgpa",
        ),
        CheckConstraint(
            "salary_stipend IS NULL OR salary_stipend >= 0.0",
            name="check_opportunity_salary_stipend",
        ),
    )

    # Relationships
    company = relationship("Company", back_populates="opportunities")
    applications = relationship(
        "Application",
        back_populates="opportunity",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Opportunity id={self.opportunity_id} title={self.title} status={self.status}>"


class Application(Base):
    """
    Table E: applications
    Connects students to opportunities in a many-to-many relationship with status tracking.
    Statuses: 'applied', 'under_review', 'shortlisted', 'interview', 'selected', 'rejected'
    Unique constraint ensures one application per student per opportunity.
    """
    __tablename__ = "applications"

    application_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="RESTRICT"),
        nullable=False,
    )
    opportunity_id = Column(
        Integer,
        ForeignKey("opportunities.opportunity_id", ondelete="RESTRICT"),
        nullable=False,
    )
    application_date = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    status = Column(String(20), nullable=False, default="applied")
    resume_path = Column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'under_review', 'shortlisted', 'interview', 'selected', 'rejected')",
            name="check_application_status",
        ),
        UniqueConstraint(
            "student_id",
            "opportunity_id",
            name="uq_student_opportunity_application",
        ),
    )

    # Relationships
    student = relationship("Student", back_populates="applications")
    opportunity = relationship("Opportunity", back_populates="applications")

    def __repr__(self) -> str:
        return f"<Application id={self.application_id} student={self.student_id} opp={self.opportunity_id} status={self.status}>"
