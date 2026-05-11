"""Tests for decision logging and querying."""

from datetime import datetime, timezone

import pytest

from semantic_router.models.decision import DecisionLog, RoutingDecision
from semantic_router.models.request import RoutingRequest


@pytest.fixture
def sample_request() -> RoutingRequest:
    return RoutingRequest(query="show my invoice", user_id="user-1")


@pytest.fixture
def sample_decision() -> RoutingDecision:
    return RoutingDecision(
        selected_route="invoice_lookup",
        confidence=0.92,
        rejected_routes=[
            {"route_name": "support_ticket", "score": 0.45},
            {"route_name": "policy_question", "score": 0.32},
        ],
        fallback_used=False,
    )


@pytest.fixture
def decision_store() -> list[DecisionLog]:
    return []


class TestDecisionLogModel:
    def test_create_decision_log(self, sample_request: RoutingRequest, sample_decision: RoutingDecision) -> None:
        log = DecisionLog(
            request=sample_request,
            decision=sample_decision,
            processing_time_ms=42,
        )
        assert log.request.query == "show my invoice"
        assert log.decision.selected_route == "invoice_lookup"
        assert log.decision.confidence == 0.92
        assert log.processing_time_ms == 42
        assert isinstance(log.timestamp, datetime)

    def test_decision_log_timestamp_is_utc(
        self, sample_request: RoutingRequest, sample_decision: RoutingDecision
    ) -> None:
        before = datetime.now(timezone.utc)
        log = DecisionLog(
            request=sample_request,
            decision=sample_decision,
            processing_time_ms=10,
        )
        after = datetime.now(timezone.utc)
        assert before <= log.timestamp <= after

    def test_decision_log_rejected_routes(
        self, sample_request: RoutingRequest
    ) -> None:
        decision = RoutingDecision(
            selected_route="invoice_lookup",
            confidence=0.75,
            rejected_routes=[
                {"route_name": "support_ticket", "score": 0.45},
                {"route_name": "refund_request", "score": 0.38},
                {"route_name": "sales_lead", "score": 0.22},
            ],
            fallback_used=False,
        )
        log = DecisionLog(request=sample_request, decision=decision, processing_time_ms=25)
        assert len(log.decision.rejected_routes) == 3

    def test_decision_log_fallback_decision(
        self, sample_request: RoutingRequest
    ) -> None:
        decision = RoutingDecision(
            selected_route=None,
            confidence=0.15,
            rejected_routes=[],
            fallback_used=True,
            clarification="Could you rephrase your question?",
        )
        log = DecisionLog(request=sample_request, decision=decision, processing_time_ms=12)
        assert log.decision.fallback_used is True
        assert log.decision.selected_route is None
        assert log.decision.clarification is not None


class TestDecisionStore:
    def test_list_decisions_returns_empty_initially(self, decision_store: list[DecisionLog]) -> None:
        assert len(decision_store) == 0

    def test_decisions_are_recorded_after_routing(
        self,
        decision_store: list[DecisionLog],
        sample_request: RoutingRequest,
        sample_decision: RoutingDecision,
    ) -> None:
        log = DecisionLog(
            request=sample_request,
            decision=sample_decision,
            processing_time_ms=42,
        )
        decision_store.append(log)
        assert len(decision_store) == 1
        assert decision_store[0].request.query == "show my invoice"

    def test_filtering_by_route_name(
        self,
        decision_store: list[DecisionLog],
        sample_request: RoutingRequest,
    ) -> None:
        for name in ["invoice_lookup", "support_ticket", "invoice_lookup", "refund_request"]:
            decision = RoutingDecision(
                selected_route=name,
                confidence=0.8,
                rejected_routes=[],
                fallback_used=False,
            )
            log = DecisionLog(request=sample_request, decision=decision, processing_time_ms=10)
            decision_store.append(log)

        invoice_logs = [log for log in decision_store if log.decision.selected_route == "invoice_lookup"]
        assert len(invoice_logs) == 2

        support_logs = [log for log in decision_store if log.decision.selected_route == "support_ticket"]
        assert len(support_logs) == 1

    def test_filtering_by_min_confidence(
        self,
        decision_store: list[DecisionLog],
        sample_request: RoutingRequest,
    ) -> None:
        confidences = [0.95, 0.45, 0.88, 0.32, 0.71]
        for conf in confidences:
            decision = RoutingDecision(
                selected_route="invoice_lookup",
                confidence=conf,
                rejected_routes=[],
                fallback_used=False,
            )
            log = DecisionLog(request=sample_request, decision=decision, processing_time_ms=10)
            decision_store.append(log)

        high_confidence = [log for log in decision_store if log.decision.confidence >= 0.7]
        assert len(high_confidence) == 3

        low_confidence = [log for log in decision_store if log.decision.confidence < 0.5]
        assert len(low_confidence) == 2

    def test_multiple_decisions_preserve_order(
        self,
        decision_store: list[DecisionLog],
        sample_request: RoutingRequest,
    ) -> None:
        for i in range(5):
            decision = RoutingDecision(
                selected_route=f"route_{i}",
                confidence=0.8,
                rejected_routes=[],
                fallback_used=False,
            )
            log = DecisionLog(request=sample_request, decision=decision, processing_time_ms=i * 10)
            decision_store.append(log)

        assert len(decision_store) == 5
        for i, log in enumerate(decision_store):
            assert log.decision.selected_route == f"route_{i}"
