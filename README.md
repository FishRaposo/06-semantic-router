# SemanticRouter

A semantic routing layer for safer, more maintainable agentic systems.

## Why SemanticRouter?

When building agentic AI systems, most teams hard-code routing logic into prompts or chain-of-thought instructions. This creates fragile, untestable, and opaque systems where a single prompt change can silently break tool selection.

**SemanticRouter moves routing outside the prompt** and into a dedicated middleware layer that combines semantic similarity, rule-based policies, confidence thresholds, and fallback logic.

## Core Concepts

### Semantic + Rules Hybrid

Routes are matched using embedding-based semantic similarity *and* evaluated against policy rules. This means:

- **Semantic matching** handles the fuzzy, natural-language side of intent detection
- **Rule-based policies** enforce hard constraints (permissions, blocked routes, approval triggers)
- **Confidence thresholds** determine when to proceed vs. when to fall back

### Confidence-Based Fallback

Every routing decision produces a confidence score. The system uses configurable thresholds:

| Confidence Range | Action |
|---|---|
| Above threshold | Route to selected tool |
| Below threshold but above minimum | Route to fallback or ask for clarification |
| Below minimum | Reject with clarification prompt |
| Policy block | Reject with reason regardless of confidence |

### Decision Transparency

Every routing decision is logged with:

- The selected route and confidence score
- All rejected routes and their scores
- Policy evaluation results
- Whether a fallback was used
- Processing time in milliseconds

## Architecture

```
User Query
    │
    ▼
┌──────────────────────┐
│   Route Registry     │  ← YAML/DB route definitions
└──────────┬───────────┘
           │
    ┌──────▼──────┐
    │  Embedding   │  ← OpenAI / sentence-transformers
    │  Service     │
    └──────┬──────┘
           │
    ┌──────▼──────────┐
    │  Semantic       │  ← Cosine similarity matching
    │  Matcher        │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Route          │  ← Confidence thresholds, tie resolution
    │  Selector       │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Policy Engine  │  ← Permissions, blocked routes, approvals
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Fallback       │  ← Low confidence / policy block handling
    │  Handler        │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │  Execution      │  → Tool adapter → Response
    │  Adapter        │
    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for dashboard)
- Docker & Docker Compose (for full stack)
- PostgreSQL with pgvector extension

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys and database URL
```

### Run with Docker Compose

```bash
docker-compose up --build
```

- API: http://localhost:8000
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Run Locally (API only)

```bash
pip install -r requirements.txt
uvicorn semantic_router.main:app --reload
```

## Configuration

### Routes (`config/routes.yaml`)

Define tools with natural-language descriptions for semantic matching:

```yaml
routes:
  - name: invoice_lookup
    description: "Look up invoice details, billing history, or payment status"
    tool_name: invoice_lookup
    confidence_threshold: 0.7
    required_permissions: ["billing.read"]
    fallback_route: support_ticket
```

### Policy (`config/policy.yaml`)

Define access rules and approval triggers:

```yaml
policy:
  blocked_routes: []
  approval_required:
    - route: refund_request
      condition: "amount > 500"
  permission_map:
    invoice_lookup: ["billing.read"]
    refund_request: ["billing.write", "finance.approve"]
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/route` | Route a user query to the best tool |
| `GET` | `/api/v1/routes` | List all registered routes |
| `POST` | `/api/v1/routes` | Register a new route |
| `GET` | `/api/v1/decisions` | Get decision log |
| `GET` | `/api/v1/health` | Health check |

## Dashboard

The Next.js dashboard provides:

- **Route Registry**: View and manage registered routes
- **Decision Log**: Browse routing decisions with confidence scores
- **Confidence Chart**: Visualize confidence distributions

## Testing

```bash
pytest tests/ -v
```

## License

MIT
