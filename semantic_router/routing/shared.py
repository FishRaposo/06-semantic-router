"""Shared singleton instances for the routing pipeline."""

from semantic_router.embedding.service import EmbeddingService
from semantic_router.execution.adapter import ExecutionAdapter
from semantic_router.policy.engine import PolicyEngine
from semantic_router.policy.fallback import FallbackHandler
from semantic_router.routing.registry import RouteRegistry
from semantic_router.routing.selector import RouteSelector
from semantic_router.routing.semantic_matcher import SemanticMatcher

_registry = RouteRegistry()
_embedding_service = EmbeddingService()
_semantic_matcher = SemanticMatcher(_embedding_service)
_selector = RouteSelector()
_policy_engine = PolicyEngine()
_fallback_handler = FallbackHandler()
_execution_adapter = ExecutionAdapter()


def get_registry() -> RouteRegistry:
    return _registry


def get_embedding_service() -> EmbeddingService:
    return _embedding_service


def get_semantic_matcher() -> SemanticMatcher:
    return _semantic_matcher


def get_selector() -> RouteSelector:
    return _selector


def get_policy_engine() -> PolicyEngine:
    return _policy_engine


def get_fallback_handler() -> FallbackHandler:
    return _fallback_handler


def get_execution_adapter() -> ExecutionAdapter:
    return _execution_adapter
