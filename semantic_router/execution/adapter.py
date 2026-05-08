"""Execution adapter for dispatching routed requests to tools."""

from semantic_router.execution.mock_tools import MOCK_TOOLS
from semantic_router.models.decision import ExecutionResult
from semantic_router.models.request import RoutingRequest
from semantic_router.models.route import Route


class ExecutionAdapter:
    """Dispatches routed requests to the appropriate tool executor."""

    def __init__(self) -> None:
        """Initialize the execution adapter with mock tools."""
        self._tools = dict(MOCK_TOOLS)

    def register_tool(self, name: str, executor: "callable") -> None:
        """Register a tool executor by name.

        Args:
            name: The tool name matching a route's tool_name.
            executor: An async callable that accepts request data and returns a result dict.
        """
        self._tools[name] = executor

    async def execute(
        self, route: Route, request: RoutingRequest
    ) -> ExecutionResult:
        """Execute the tool associated with the given route.

        Args:
            route: The selected route with tool_name.
            request: The original routing request.

        Returns:
            An ExecutionResult with the tool's output or error.
        """
        executor = self._tools.get(route.tool_name)
        if executor is None:
            return ExecutionResult(
                tool_name=route.tool_name,
                status="error",
                error=f"No executor registered for tool '{route.tool_name}'",
            )

        try:
            result = await executor(query=request.query, context=request.context or {})
            return ExecutionResult(
                tool_name=route.tool_name,
                status="success",
                data=result,
            )
        except Exception as exc:
            return ExecutionResult(
                tool_name=route.tool_name,
                status="error",
                error=str(exc),
            )
