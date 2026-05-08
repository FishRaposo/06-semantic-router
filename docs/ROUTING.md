# Routing

## How Routing Works

SemanticRouter uses a multi-stage pipeline to select the right tool for a user query.

## Stage 1: Semantic Matching

The query is embedded and compared against pre-computed route description embeddings using cosine similarity.

```python
score = cosine_similarity(query_embedding, route_embedding)
```

Each route produces a `RouteMatch` with:
- `route_name`: The matched route
- `score`: Cosine similarity (0.0 to 1.0)
- `description`: The route's natural-language description

The matcher returns the top-k candidates (default k=5).

## Stage 2: Route Selection

The `RouteSelector` evaluates the top matches against confidence thresholds:

| Threshold | Default | Purpose |
|---|---|---|
| `confidence_threshold` | 0.7 | Minimum score to auto-select a route |
| `min_confidence` | 0.3 | Minimum score to consider a fallback |
| Below `min_confidence` | — | No match, generate clarification |

### Tie Resolution

When multiple routes have similar scores (within 0.05), the selector:

1. Checks if the user context disambiguates (e.g., recent route history).
2. Falls back to the route with the higher base confidence threshold.
3. Returns a clarification prompt if still ambiguous.

## Stage 3: LLM Classifier (Optional)

For ambiguous queries, an optional LLM classifier can be invoked:

- Receives the query and top-k route candidates.
- Returns a single `RouteMatch` with an LLM-generated confidence score.
- Higher latency but better disambiguation for complex queries.

## Stage 4: Policy Evaluation

Before execution, the selected route passes through the policy engine (see [POLICY.md](./POLICY.md)).

## Stage 5: Fallback

If any stage fails, the fallback handler determines the appropriate response (see [CONFIDENCE.md](./CONFIDENCE.md)).

## Route Definition

Each route is defined with:

```yaml
- name: invoice_lookup
  description: "Look up invoice details, billing history, or payment status"
  tool_name: invoice_lookup
  confidence_threshold: 0.7
  required_permissions: ["billing.read"]
  fallback_route: support_ticket
  metadata:
    category: billing
    priority: high
```

- **name**: Unique identifier for the route.
- **description**: Natural-language description used for semantic matching.
- **tool_name**: The actual tool/workflow to invoke.
- **confidence_threshold**: Minimum confidence to auto-select this route.
- **required_permissions**: List of permissions required to access this route.
- **fallback_route**: Route to use if confidence is too low.
- **metadata**: Optional key-value pairs for categorization.
