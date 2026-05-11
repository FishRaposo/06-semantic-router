"""Initial database migration — decision_logs table.

Revision ID: 001
Revises: None
Create Date: 2026-05-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decision_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_query", sa.String(1024), nullable=False),
        sa.Column("request_user_id", sa.String(256), nullable=True),
        sa.Column("request_context", postgresql.JSONB, nullable=True),
        sa.Column("request_metadata", postgresql.JSONB, nullable=True),
        sa.Column("selected_route", sa.String(256), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("rejected_routes", postgresql.JSONB, nullable=True),
        sa.Column("policy_check", postgresql.JSONB, nullable=True),
        sa.Column("fallback_used", sa.Boolean(), nullable=False),
        sa.Column("clarification", sa.Text(), nullable=True),
        sa.Column("execution_result", postgresql.JSONB, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processing_time_ms", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("decision_logs")
