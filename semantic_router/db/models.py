"""SQLAlchemy models for database persistence."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


class DecisionLogModel(Base):
    """Persisted record of a routing decision."""

    __tablename__ = "decision_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_query: Mapped[str] = mapped_column(String(1024), nullable=False)
    request_user_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    request_context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    request_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    selected_route: Mapped[str | None] = mapped_column(String(256), nullable=True)
    confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)
    rejected_routes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    policy_check: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    fallback_used: Mapped[bool] = mapped_column(nullable=False, default=False)
    clarification: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
