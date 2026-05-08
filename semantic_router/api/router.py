"""Main routing endpoint that processes user queries."""

import time

from fastapi import APIRouter

from semantic_router.embedding.service import EmbeddingService
from semantic_router.execution.adapter import ExecutionAdapter
from semantic_router.models.decision import DecisionLog, RoutingDecision
from semantic_router.models.request import RoutingRequest
from semantic_router.policy.engine import PolicyEngine
from semantic_router.policy.fallback import FallbackHandler
from semantic_router.routing.registry import RouteRegistry
from semantic_router.routing.selector import RouteSelector
from semantic_router.routing.semantic_matcher import SemanticMatcher

router = APIRouter()

registry = RouteRegistry()
embedding_service = EmbeddingService()
semantic_matcher = SemanticMatcher(embedding_service)
selector = RouteSelector()
policy_engine = PolicyEngine()
fallback_handler = FallbackHandler()
execution_adapter = ExecutionAdapter()


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
        return fallback_handler.handle_low_confidence(request, decision, processing_time_ms)

    policy_result = policy_engine.evaluate(
        route=registry.get_route(decision.selected_route),
        context=request.context or {},
    )
    decision.policy_check = policy_result

    if not policy_result.allowed:
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        return fallback_handler.handle_policy_block(request, decision, policy_result, processing_time_ms)

    selected_route = registry.get_route(decision.selected_route)
    if selected_route is not None:
        execution_result = await execution_adapter.execute(route=selected_route, request=request)
        decision.execution_result = execution_result

    processing_time_ms = int((time.perf_counter() - start_time) * 1000)
    _log = DecisionLog(
        request=request,
        decision=decision,
        processing_time_ms=processing_time_ms,
    )

    return decision
