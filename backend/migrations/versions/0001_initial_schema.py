"""Initial schema: users, students, companies, opportunities, applications

Baseline revision. Databases created before Alembic was introduced are
stamped at this revision by app.database.upgrade_db and then upgraded.

Revision ID: 0001
Revises:
Create Date: 2026-10-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("company_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("location", sa.String(150), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
    )
    op.create_index("ix_companies_company_id", "companies", ["company_id"])

    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("account_status", sa.String(20), nullable=False),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.company_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('student', 'recruiter', 'admin')", name="check_user_role"),
        sa.CheckConstraint(
            "account_status IN ('active', 'disabled')", name="check_user_account_status"
        ),
    )
    op.create_index("ix_users_user_id", "users", ["user_id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "students",
        sa.Column("student_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("cgpa", sa.Float(), nullable=False),
        sa.Column("graduation_year", sa.Integer(), nullable=False),
        sa.CheckConstraint("cgpa >= 0.0 AND cgpa <= 10.0", name="check_student_cgpa"),
    )
    op.create_index("ix_students_student_id", "students", ["student_id"])

    op.create_table(
        "opportunities",
        sa.Column("opportunity_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.company_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("opportunity_type", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(150), nullable=True),
        sa.Column("salary_stipend", sa.Float(), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=False),
        sa.Column("eligibility_cgpa", sa.Float(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "opportunity_type IN ('internship', 'full_time', 'part_time')",
            name="check_opportunity_type",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'open', 'closed')", name="check_opportunity_status"
        ),
        sa.CheckConstraint(
            "eligibility_cgpa >= 0.0 AND eligibility_cgpa <= 10.0",
            name="check_opportunity_eligibility_cgpa",
        ),
        sa.CheckConstraint(
            "salary_stipend IS NULL OR salary_stipend >= 0.0",
            name="check_opportunity_salary_stipend",
        ),
    )
    op.create_index("ix_opportunities_opportunity_id", "opportunities", ["opportunity_id"])

    op.create_table(
        "applications",
        sa.Column("application_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "student_id",
            sa.Integer(),
            sa.ForeignKey("students.student_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "opportunity_id",
            sa.Integer(),
            sa.ForeignKey("opportunities.opportunity_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("application_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("resume_path", sa.String(500), nullable=True),
        sa.CheckConstraint(
            "status IN ('applied', 'under_review', 'shortlisted', 'interview', 'selected', 'rejected')",
            name="check_application_status",
        ),
        sa.UniqueConstraint(
            "student_id", "opportunity_id", name="uq_student_opportunity_application"
        ),
    )
    op.create_index("ix_applications_application_id", "applications", ["application_id"])


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("opportunities")
    op.drop_table("students")
    op.drop_table("users")
    op.drop_table("companies")
