# Contributing to SemanticRouter

## Architecture Overview

SemanticRouter is a semantic routing layer that sits between user queries and backend tools. It uses embedding-based similarity matching to route natural-language requests to the most appropriate tool, with confidence thresholds, policy enforcement, and fallback handling.

### Package Structure

```
semantic_router/
  api/            FastAPI endpoints (health, routes, router)
  embedding/      Embedding service (OpenAI, sentence-transformers)
  execution/      Tool execution adapter and mock tools
  models/         Pydantic models (Route, RoutingRequest, RoutingDecision, DecisionLog)
  policy/         Policy engine, permission checker, fallback handler
  routing/        Route registry, semantic matcher, route selector, LLM classifier
```

### Pipeline Flow

1. **Request arrives** at `POST /api/v1/route` with a `RoutingRequest` containing the user's query and optional context.
2. **Semantic Matcher** embeds the query and computes cosine similarity against all registered route descriptions.
3. **Route Selector** picks the best match, applying confidence thresholds, tie resolution, and fallback logic.
4. **Policy Engine** checks the selected route against user permissions and approval rules.
5. **Execution Adapter** dispatches to the appropriate tool and returns results.
6. **Decision Log** records the full routing trace with timestamp and processing time.

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| RouteRegistry | `routing/registry.py` | In-memory route storage with YAML loading |
| SemanticMatcher | `routing/semantic_matcher.py` | Cosine-similarity matching via embeddings |
| RouteSelector | `routing/selector.py` | Confidence threshold and tie resolution |
| LLMClassifier | `routing/classifier.py` | Optional LLM-based route disambiguation |
| PolicyEngine | `policy/engine.py` | Permission and approval rule evaluation |
| FallbackHandler | `policy/fallback.py` | No-match, low-confidence, policy-block handling |
| EmbeddingService | `embedding/service.py` | OpenAI and sentence-transformers backends |
| ExecutionAdapter | `execution/adapter.py` | Tool dispatch with mock tool support |

## How to Add a New Route

1. Add a route definition to `config/routes.example.yaml`:

```yaml
routes:
  - name: my_new_route
    description: Natural language description for semantic matching
    tool_name: my_new_route
    confidence_threshold: 0.7
    required_permissions: ["my.permission"]
    fallback_route: null
    metadata:
      category: custom
```

2. Register it programmatically via `POST /api/v1/routes`:

```json
{
  "name": "my_new_route",
  "description": "Natural language description for semantic matching",
  "tool_name": "my_new_route",
  "confidence_threshold": 0.7,
  "required_permissions": ["my.permission"]
}
```

3. If using the in-memory registry, pass the YAML config at startup via the `ROUTES_CONFIG` env var.

## How to Add a New Tool

1. Create an async tool function in `semantic_router/execution/mock_tools.py` (for mock tools) or in your own module:

```python
async def my_new_tool(query: str, context: dict) -> dict[str, Any]:
    return {"result": f"Processed: {query}"}
```

2. Register the tool in `MOCK_TOOLS` dictionary or via `ExecutionAdapter.register_tool()`:

```python
execution_adapter.register_tool("my_new_route", my_new_tool)
```

3. The `tool_name` field in your route definition must match the registered tool name.

## How to Add a Policy Rule

Add rules to `config/policy.example.yaml`:

```yaml
policy:
  blocked_routes:
    - deprecated_route
  permission_map:
    invoice_lookup: ["billing.read"]
    refund_request: ["billing.write", "finance.approve"]
  approval_required:
    - route: refund_request
      condition: "amount > 500"
      message: "Manager approval needed for large refunds"
```

## Testing

### Running Tests

```bash
# Full test suite with coverage
make test

# Specific test file
python -m pytest tests/test_registry.py -v

# Single test
python -m pytest tests/test_registry.py::TestRouteRegistry::test_register_route -v
```

### Test Structure

| File | Covers |
|------|--------|
| `test_registry.py` | Route registration, retrieval, YAML loading |
| `test_semantic_matcher.py` | Embedding-based matching with mock embeddings |
| `test_policy.py` | Policy evaluation, permissions, blocked routes |
| `test_fallback.py` | No-match, low-confidence, policy-block handling |
| `test_classifier.py` | LLM classifier disambiguation and fallback |
| `test_decisions.py` | Decision logging and querying |
| `test_integration.py` | End-to-end pipeline tests |

### Test Fixtures

Shared fixtures are in `conftest.py`:
- `sample_routes` — Five sample business routes
- `populated_registry` — Registry with sample routes loaded

### Writing New Tests

- Use `pytest.mark.asyncio` for async tests
- Use `MockEmbeddingService` from `test_semantic_matcher.py` for deterministic embeddings
- Use `IntegrationEmbeddingService` from `test_integration.py` for keyword-matched embeddings
- Policy and fallback tests should use direct class instantiation

## Code Quality

```bash
# Lint and type check
make lint

# Auto-format
make format
```

- **Ruff**: Linting and formatting (config in `pyproject.toml`)
- **Mypy**: Static type checking (strict mode, config in `pyproject.toml`)
- **Prettier**: Dashboard code formatting
- **Pre-commit**: Run `pre-commit install` to enable git hooks

## Development Setup

```bash
# First-time setup (creates venv, installs deps, starts services, seeds data)
make setup

# Or step by step:
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make install
make dev
make seed
```
