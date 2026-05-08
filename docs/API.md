# API Reference

Base URL: `http://localhost:8000`

## Route Query

### `POST /api/v1/route`

Route a user query to the best-matching tool.

**Request Body:**

```json
{
  "query": "What's the status of invoice #12345?",
  "context": {
    "session_id": "abc-123"
  },
  "user_id": "user-456",
  "metadata": {}
}
```

**Response (200):**

```json
{
  "selected_route": "invoice_lookup",
  "confidence": 0.92,
  "rejected_routes": [
    {"route_name": "support_ticket", "score": 0.45},
    {"route_name": "policy_question", "score": 0.31}
  ],
  "policy_check": {
    "allowed": true,
    "reason": null,
    "required_action": null
  },
  "fallback_used": false,
  "execution_result": {
    "tool_name": "invoice_lookup",
    "status": "success",
    "data": { "invoice_id": "12345", "status": "paid" },
    "error": null
  }
}
```

**Response (200, low confidence):**

```json
{
  "selected_route": null,
  "confidence": 0.35,
  "rejected_routes": [],
  "policy_check": {
    "allowed": false,
    "reason": "Confidence below threshold",
    "required_action": "clarify"
  },
  "fallback_used": true,
  "clarification": "Could you clarify what you need help with?"
}
```

## Route Management

### `GET /api/v1/routes`

List all registered routes.

**Response (200):**

```json
[
  {
    "name": "invoice_lookup",
    "description": "Look up invoice details, billing history, or payment status",
    "tool_name": "invoice_lookup",
    "confidence_threshold": 0.7,
    "required_permissions": ["billing.read"],
    "fallback_route": "support_ticket"
  }
]
```

### `POST /api/v1/routes`

Register a new route.

**Request Body:**

```json
{
  "name": "new_tool",
  "description": "Description for semantic matching",
  "tool_name": "new_tool",
  "confidence_threshold": 0.7,
  "required_permissions": [],
  "fallback_route": null
}
```

**Response (201):** The created route object.

## Decision Log

### `GET /api/v1/decisions`

Retrieve routing decision history.

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| `limit` | int | Max decisions to return (default 50) |
| `offset` | int | Pagination offset |
| `route` | str | Filter by selected route name |
| `min_confidence` | float | Filter by minimum confidence |

**Response (200):**

```json
{
  "decisions": [
    {
      "request": { "query": "...", "user_id": "..." },
      "decision": {
        "selected_route": "invoice_lookup",
        "confidence": 0.92,
        "fallback_used": false
      },
      "timestamp": "2025-01-15T10:30:00Z",
      "processing_time_ms": 45
    }
  ],
  "total": 150
}
```

## Health

### `GET /api/v1/health`

Health check endpoint.

**Response (200):**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "routes_loaded": 5,
  "embedding_service": "openai"
}
```
