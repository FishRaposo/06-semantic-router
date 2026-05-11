"""Main routing endpoint that processes user queries."""

import logging
import time

from fastapi import APIRouter

from semantic_router.db import async_session
from semantic_router.db.models import DecisionLogModel
from semantic_router.models.decision import RoutingDecision
from semantic_router.models.request import RoutingRequest
from semantic_router.routing.shared import (
    get_embedding_service,
    get_execution_adapter,
    get_fallback_handler,
    get_policy_engine,
    get_registry,
    get_selector,
    get_semantic_matcher,
)

router = APIRouter()
logger = logging.getLogger(__name__)

registry = get_registry()
embedding_service = get_embedding_service()
semantic_matcher = get_semantic_matcher()
selector = get_selector()
policy_engine = get_policy_engine()
fallback_handler = get_fallback_handler()
execution_adapter = get_execution_adapter()


async def _persist_log(
    request: RoutingRequest, decision: RoutingDecision, processing_time_ms: int
) -> None:
    try:
        async with async_session() as session:
            log = DecisionLogModel(
                request_query=request.query,
                request_user_id=request.user_id,
                request_context=request.context,
                request_metadata=request.metadata,
                selected_route=decision.selected_route,
                confidence=decision.confidence,
                rejected_routes=decision.rejected_routes if decision.rejected_routes else None,
                policy_check=decision.policy_check.model_dump() if decision.policy_check else None,
                fallback_used=decision.fallback_used,
                clarification=decision.clarification,
                execution_result=(
                    decision.execution_result.model_dump() if decision.execution_result else None
                ),
                processing_time_ms=processing_time_ms,
            )
            session.add(log)
            await session.commit()
    except Exception:
        logger.exception("Failed to persist decision log to database")


@router.post("/route", response_model=RoutingDecision)
async def route_request(request: RoutingRequest) -> RoutingDecision:
    """Route a user query to the best-matching tool based on semantic intent."""
    start_time = time.perf_counter()

    routes = registry.list_routes()
    if not routes:
        return fallback_handler.handle_no_match(request)

    matches = await semantic_matcher.match(query=request.query, routes=routes, top_k=5)
    decision = selector.select(matches=matches, context=request.context or {}, routes=routes)

    if decision.selected_route is None:
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        result = fallback_handler.handle_low_confidence(request, decision, processing_time_ms)
        await _persist_log(request, result, processing_time_ms)
        return result

    policy_result = policy_engine.evaluate(
        route=registry.get_route(decision.selected_route),
        context=request.context or {},
    )
    decision.policy_check = policy_result

    if not policy_result.allowed:
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        result = fallback_handler.handle_policy_block(
            request, decision, policy_result, processing_time_ms
        )
        await _persist_log(request, result, processing_time_ms)
        return result

    selected_route = registry.get_route(decision.selected_route)
    if selected_route is not None:
        execution_result = await execution_adapter.execute(route=selected_route, request=request)
        decision.execution_result = execution_result

    processing_time_ms = int((time.perf_counter() - start_time) * 1000)
    await _persist_log(request, decision, processing_time_ms)

    return decision
