"""Route selector with confidence thresholds and tie resolution."""

from semantic_router.config import settings
from semantic_router.models.decision import RoutingDecision
from semantic_router.models.route import Route
from semantic_router.routing.semantic_matcher import RouteMatch


class RouteSelector:
    """Selects the best route from semantic matches using confidence thresholds."""

    def __init__(
        self,
        default_threshold: float | None = None,
        min_threshold: float | None = None,
        tie_margin: float = 0.05,
    ) -> None:
        """Initialize the route selector.

        Args:
            default_threshold: Default confidence threshold for route selection.
            min_threshold: Minimum confidence threshold below which no route is selected.
            tie_margin: Margin within which two scores are considered a tie.
        """
        self._default_threshold = default_threshold or settings.default_confidence_threshold
        self._min_threshold = min_threshold or settings.min_confidence_threshold
        self._tie_margin = tie_margin

    def select(
        self,
        matches: list[RouteMatch],
        context: dict,
        routes: list[Route],
    ) -> RoutingDecision:
        """Select the best route from semantic match results.

        Args:
            matches: Ranked list of route matches from semantic matching.
            context: Routing context with user permissions and session data.
            routes: All registered routes for threshold lookup.

        Returns:
            A RoutingDecision with the selected route or fallback indication.
        """
        if not matches:
            return RoutingDecision(
                selected_route=None,
                confidence=0.0,
                rejected_routes=[],
                fallback_used=False,
            )

        route_thresholds = {r.name: r.confidence_threshold for r in routes}
        best = matches[0]
        threshold = route_thresholds.get(best.route_name, self._default_threshold)

        rejected: list[dict[str, str | float]] = [
            {"route_name": m.route_name, "score": m.score} for m in matches[1:]
        ]

        if len(matches) >= 2 and (matches[0].score - matches[1].score) < self._tie_margin:
            return RoutingDecision(
                selected_route=None,
                confidence=best.score,
                rejected_routes=rejected,
                fallback_used=False,
                clarification=self._generate_tie_clarification(matches[:2]),
            )

        if best.score < self._min_threshold:
            return RoutingDecision(
                selected_route=None,
                confidence=best.score,
                rejected_routes=rejected,
                fallback_used=False,
            )

        if best.score < threshold:
            fallback_route = self._find_fallback(matches, routes)
            if fallback_route:
                return RoutingDecision(
                    selected_route=fallback_route.name,
                    confidence=best.score,
                    rejected_routes=rejected,
                    fallback_used=True,
                )
            return RoutingDecision(
                selected_route=None,
                confidence=best.score,
                rejected_routes=rejected,
                fallback_used=False,
            )

        return RoutingDecision(
            selected_route=best.route_name,
            confidence=best.score,
            rejected_routes=rejected,
            fallback_used=False,
        )

    def _find_fallback(self, matches: list[RouteMatch], routes: list[Route]) -> Route | None:
        """Find the configured fallback route for the best match.

        Args:
            matches: Ranked list of route matches.
            routes: All registered routes.

        Returns:
            The fallback Route if configured and exists, else None.
        """
        best_name = matches[0].route_name
        route_map = {r.name: r for r in routes}
        best_route = route_map.get(best_name)
        if best_route and best_route.fallback_route:
            return route_map.get(best_route.fallback_route)
        return None

    def _generate_tie_clarification(self, tied: list[RouteMatch]) -> str:
        """Generate a clarification prompt for tied matches.

        Args:
            tied: The tied route matches.

        Returns:
            A clarification prompt string.
        """
        options = " or ".join(f"[{m.route_name}]" for m in tied)
        return f"I'm not sure if you want {options}. Could you clarify?"
