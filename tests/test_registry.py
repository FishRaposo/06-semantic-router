"""Tests for the RouteRegistry."""

import tempfile
from pathlib import Path

import pytest
import yaml

from semantic_router.models.route import Route
from semantic_router.routing.registry import RouteRegistry


class TestRouteRegistry:
    """Tests for route registration, retrieval, and YAML loading."""

    def test_register_route(self) -> None:
        """Registering a route stores it in the registry."""
        registry = RouteRegistry()
        route = Route(
            name="test_route",
            description="A test route",
            tool_name="test_tool",
            confidence_threshold=0.7,
        )
        registry.register_route(route)
        assert registry.get_route("test_route") is route

    def test_register_route_overwrites_existing(self) -> None:
        """Registering a route with the same name overwrites the previous one."""
        registry = RouteRegistry()
        route_v1 = Route(name="test", description="v1", tool_name="t", confidence_threshold=0.5)
        route_v2 = Route(name="test", description="v2", tool_name="t", confidence_threshold=0.7)
        registry.register_route(route_v1)
        registry.register_route(route_v2)
        assert registry.get_route("test") is route_v2

    def test_get_route_not_found(self) -> None:
        """Getting a non-existent route returns None."""
        registry = RouteRegistry()
        assert registry.get_route("missing") is None

    def test_list_routes_empty(self) -> None:
        """Listing routes on empty registry returns empty list."""
        registry = RouteRegistry()
        assert registry.list_routes() == []

    def test_list_routes_returns_all(self, populated_registry: RouteRegistry) -> None:
        """Listing routes returns all registered routes."""
        routes = populated_registry.list_routes()
        assert len(routes) == 5
        names = {r.name for r in routes}
        assert names == {"invoice_lookup", "support_ticket", "refund_request", "policy_question", "sales_lead"}

    def test_remove_route(self) -> None:
        """Removing a route deletes it from the registry."""
        registry = RouteRegistry()
        route = Route(name="test", description="test", tool_name="t", confidence_threshold=0.5)
        registry.register_route(route)
        assert registry.remove_route("test") is True
        assert registry.get_route("test") is None

    def test_remove_route_not_found(self) -> None:
        """Removing a non-existent route returns False."""
        registry = RouteRegistry()
        assert registry.remove_route("missing") is False

    def test_load_from_yaml(self) -> None:
        """Loading routes from a YAML file populates the registry."""
        yaml_data = {
            "routes": [
                {
                    "name": "yaml_route",
                    "description": "A route from YAML",
                    "tool_name": "yaml_tool",
                    "confidence_threshold": 0.75,
                    "required_permissions": ["test.read"],
                    "fallback_route": None,
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.dump(yaml_data, f)
            f.flush()
            path = f.name

        try:
            registry = RouteRegistry()
            registry.load_from_yaml(path)
            route = registry.get_route("yaml_route")
            assert route is not None
            assert route.tool_name == "yaml_tool"
            assert route.confidence_threshold == 0.75
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_from_yaml_missing_file(self) -> None:
        """Loading from a non-existent YAML file does not raise."""
        registry = RouteRegistry()
        registry.load_from_yaml("/nonexistent/path.yaml")
        assert registry.list_routes() == []

    def test_get_route_embeddings(self, populated_registry: RouteRegistry) -> None:
        """Getting route embeddings returns a mapping of route names to embeddings."""
        embeddings = populated_registry.get_route_embeddings()
        assert len(embeddings) == 5
        for name in ["invoice_lookup", "support_ticket", "refund_request", "policy_question", "sales_lead"]:
            assert name in embeddings
            assert embeddings[name] is None
