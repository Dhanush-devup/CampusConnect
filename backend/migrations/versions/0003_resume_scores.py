"""Add resume_scores table for ATS resume scoring

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resume_scores",
        sa.Column("score_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.application_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("skills_score", sa.Integer(), nullable=True),
        sa.Column("experience_score", sa.Integer(), nullable=True),
        sa.Column("education_score", sa.Integer(), nullable=True),
        sa.Column("formatting_score", sa.Integer(), nullable=True),
        sa.Column("matched_skills", sa.Text(), nullable=True),
        sa.Column("missing_skills", sa.Text(), nullable=True),
        sa.Column("strengths", sa.Text(), nullable=True),
        sa.Column("improvements", sa.Text(), nullable=True),
        sa.Column("flags", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("scored_by", sa.String(20), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'completed', 'failed')", name="check_resume_score_status"
        ),
        sa.CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)",
            name="check_resume_score_range",
        ),
    )
    op.create_index("ix_resume_scores_score_id", "resume_scores", ["score_id"])


def downgrade() -> None:
    op.drop_table("resume_scores")
