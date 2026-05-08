"""Route registry for managing registered routes."""

import yaml
from pathlib import Path

from semantic_router.models.route import Route, RouteConfig


class RouteRegistry:
    """In-memory registry for route definitions with YAML loading support."""

    def __init__(self) -> None:
        """Initialize an empty route registry."""
        self._routes: dict[str, Route] = {}

    def register_route(self, route: Route) -> None:
        """Register a route in the registry.

        Args:
            route: The route to register.
        """
        self._routes[route.name] = route

    def get_route(self, name: str) -> Route | None:
        """Retrieve a route by name.

        Args:
            name: The unique name of the route.

        Returns:
            The route if found, or None.
        """
        return self._routes.get(name)

    def list_routes(self) -> list[Route]:
        """Return all registered routes.

        Returns:
            A list of all registered routes.
        """
        return list(self._routes.values())

    def remove_route(self, name: str) -> bool:
        """Remove a route from the registry.

        Args:
            name: The name of the route to remove.

        Returns:
            True if the route was removed, False if not found.
        """
        if name in self._routes:
            del self._routes[name]
            return True
        return False

    def load_from_yaml(self, path: str | Path) -> None:
        """Load routes from a YAML configuration file.

        Args:
            path: Path to the YAML file containing route definitions.
        """
        file_path = Path(path)
        if not file_path.exists():
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "routes" not in data:
            return

        for route_data in data["routes"]:
            config = RouteConfig(**route_data)
            route = Route(**config.model_dump())
            self.register_route(route)

    def get_route_embeddings(self) -> dict[str, list[float] | None]:
        """Return a mapping of route names to their embedding vectors.

        Returns:
            Dictionary mapping route names to embedding vectors or None.
        """
        return {name: route.embedding for name, route in self._routes.items()}
