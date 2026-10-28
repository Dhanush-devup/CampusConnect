"""Add 'pending' account status; enforce RESTRICT foreign keys

1. users.account_status now allows 'pending' (recruiters awaiting admin approval).
2. Databases created by an older version of the models have ON DELETE CASCADE on
   opportunities.company_id and applications.student_id / opportunity_id, so
   deleting a company silently wiped its jobs and applications. These tables are
   rebuilt with ON DELETE RESTRICT to match app.models. On databases that already
   have RESTRICT the rebuild is a no-op apart from copying rows.

SQLite cannot alter constraints in place, so each table is rebuilt from an explicit
definition (copy_from) instead of relying on reflection.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def users_table(account_statuses: str) -> sa.Table:
    return sa.Table(
        "users",
        sa.MetaData(),
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
            f"account_status IN ({account_statuses})", name="check_user_account_status"
        ),
    )


def opportunities_table() -> sa.Table:
    return sa.Table(
        "opportunities",
        sa.MetaData(),
        sa.Column(
            "opportunity_id", sa.Integer(), primary_key=True, autoincrement=True
        ),
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


def applications_table() -> sa.Table:
    return sa.Table(
        "applications",
        sa.MetaData(),
        sa.Column(
            "application_id", sa.Integer(), primary_key=True, autoincrement=True
        ),
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


# Indexes are dropped along with the old table and are not carried over by the
# batch copy, so they are recreated explicitly after each rebuild.
TABLE_INDEXES = {
    "users": [("ix_users_user_id", ["user_id"], False), ("ix_users_email", ["email"], True)],
    "opportunities": [("ix_opportunities_opportunity_id", ["opportunity_id"], False)],
    "applications": [("ix_applications_application_id", ["application_id"], False)],
}


def rebuild(table: sa.Table) -> None:
    with op.batch_alter_table(table.name, copy_from=table, recreate="always"):
        pass
    for name, columns, unique in TABLE_INDEXES[table.name]:
        op.create_index(name, table.name, columns, unique=unique)


def upgrade() -> None:
    rebuild(users_table("'pending', 'active', 'disabled'"))
    rebuild(opportunities_table())
    rebuild(applications_table())


def downgrade() -> None:
    # 'pending' no longer exists below this revision; keep those accounts locked out
    op.execute("UPDATE users SET account_status = 'disabled' WHERE account_status = 'pending'")
    rebuild(users_table("'active', 'disabled'"))
