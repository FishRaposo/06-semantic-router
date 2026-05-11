"""Decision log retrieval endpoints."""

import logging

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from semantic_router.db import async_session
from semantic_router.db.models import DecisionLogModel
from semantic_router.models.decision import (
    DecisionLog,
    ExecutionResult,
    PolicyCheck,
    RoutingDecision,
)
from semantic_router.models.request import RoutingRequest

router = APIRouter()
logger = logging.getLogger(__name__)


def _row_to_decision_log(row: DecisionLogModel) -> DecisionLog:
    return DecisionLog(
        request=RoutingRequest(
            query=row.request_query,
            user_id=row.request_user_id,
            context=row.request_context,
            metadata=row.request_metadata or {},
        ),
        decision=RoutingDecision(
            selected_route=row.selected_route,
            confidence=row.confidence,
            rejected_routes=row.rejected_routes or [],
            policy_check=PolicyCheck(**row.policy_check) if row.policy_check else None,
            fallback_used=row.fallback_used,
            clarification=row.clarification,
            execution_result=(
                ExecutionResult(**row.execution_result) if row.execution_result else None
            ),
        ),
        timestamp=row.timestamp,
        processing_time_ms=row.processing_time_ms,
    )


@router.get("/decisions")
async def get_decisions(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict:
    try:
        async with async_session() as session:
            count_query = select(func.count()).select_from(DecisionLogModel)
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            query = (
                select(DecisionLogModel)
                .order_by(DecisionLogModel.timestamp.desc())
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            rows = result.scalars().all()
            return {"decisions": [_row_to_decision_log(row) for row in rows], "total": total}
    except Exception:
        logger.exception("Failed to query decision logs")
        return {"decisions": [], "total": 0}
