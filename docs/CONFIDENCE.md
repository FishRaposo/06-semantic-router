# Confidence & Fallback

## Confidence Scoring

Every routing decision includes a confidence score derived from cosine similarity between the query embedding and route description embedding.

### Score Ranges

| Range | Label | Action |
|---|---|---|
| 0.85 - 1.0 | High | Auto-route to selected tool |
| 0.70 - 0.85 | Good | Route with logged confidence |
| 0.50 - 0.70 | Low | Route to fallback or request clarification |
| 0.30 - 0.50 | Very Low | Generate clarification prompt |
| 0.00 - 0.30 | No Match | Reject with "unable to understand" response |

These are defaults. Each route can override `confidence_threshold` independently.

## Fallback Strategies

### 1. Route Fallback

If the selected route's confidence is below its threshold, the system checks for a configured `fallback_route`:

```yaml
- name: refund_request
  confidence_threshold: 0.8
  fallback_route: support_ticket
```

The fallback route is matched and policy-checked independently.

### 2. Clarification Prompt

When confidence is very low or multiple routes are tied, the system generates a clarification prompt:

```
"I'm not sure if you want to [action A] or [action B]. Could you clarify?"
```

### 3. Policy Block Fallback

When a route is policy-blocked, the fallback handler:

1. Checks if the next-best match is allowed.
2. If no allowed match exists, returns the policy rejection reason.
3. Logs the policy block for analytics.

### 4. No Match

When no route scores above the minimum confidence:

```
"I couldn't find a matching tool for your request. Please try rephrasing."
```

## Tuning Confidence

### Per-Route Thresholds

Routes with higher risk (e.g., refunds) should have higher thresholds:

```yaml
- name: invoice_lookup
  confidence_threshold: 0.6

- name: refund_request
  confidence_threshold: 0.85
```

### Embedding Model Selection

Confidence quality depends on the embedding model:

- **OpenAI text-embedding-3-small**: Better for general-purpose queries, higher confidence scores.
- **sentence-transformers all-MiniLM-L6-v2**: Good for domain-specific descriptions, lower latency.

### Route Description Quality

Better descriptions produce better embeddings:

- Use specific, action-oriented language.
- Include synonyms and common phrasings.
- Mention concrete objects (e.g., "invoice" not "document").

## Confidence Analytics

The dashboard tracks:

- Distribution of confidence scores across all decisions.
- Routes with the highest average confidence (well-described).
- Routes with the lowest average confidence (need better descriptions).
- Fallback frequency per route.
