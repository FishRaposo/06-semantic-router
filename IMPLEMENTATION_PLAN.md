# Implementation Plan

## Phase 1: Core Routing (Weeks 1-2)

**Goal**: Route registry, embedding-based semantic matching, basic routing endpoint, mock tools.

### Deliverables

- [x] **Route Registry**: In-memory and YAML-backed route storage with `register_route()`, `get_route()`, `list_routes()`, `load_from_yaml()`, `get_route_embeddings()`.
- [x] **Embedding Service**: Abstraction over OpenAI and sentence-transformers with `embed()` and `embed_batch()` methods. Caching support for route embeddings.
- [x] **Semantic Matcher**: Cosine-similarity matching between query embeddings and route description embeddings. Returns top-k candidates with scores.
- [x] **Routing Endpoint**: `POST /api/v1/route` accepting a `RoutingRequest` and returning a `RoutingDecision`.
- [x] **Mock Tools**: Five mock business tools (invoice_lookup, support_ticket, refund_request, policy_question, sales_lead) with typed schemas.
- [x] **Execution Adapter**: Generic adapter interface that dispatches to mock tools.
- [x] **Tests**: `test_registry.py`, `test_semantic_matcher.py` with mock embeddings.

### Exit Criteria

- Can register routes from YAML and match user queries to the correct tool via embeddings.
- All mock tools return typed responses through the execution adapter.
- Test coverage > 80% for routing and registry modules.

---

## Phase 2: Policy & Confidence (Weeks 3-4)

**Goal**: Confidence thresholds, policy engine, fallback logic, LLM classifier option, decision logging.

### Deliverables

- [x] **Route Selector**: Confidence-threshold-based selection with tie resolution. Produces `RoutingDecision` with rejected routes and fallback status.
- [x] **Policy Engine**: Rule evaluation against route + context. Supports blocked routes, required permissions, and approval triggers.
- [x] **Permission Checker**: User permission resolution from context. Integration with policy engine for access control.
- [x] **Fallback Handler**: Handles no-match, low-confidence, and policy-block scenarios. Generates clarification prompts for ambiguous queries.
- [x] **LLM Classifier** (optional): Alternative or supplementary classifier using an LLM call for disambiguation.
- [x] **Decision Logging**: Persist every routing decision with request, decision, timestamp, and processing time. PostgreSQL storage.
- [x] **Tests**: `test_policy.py`, `test_fallback.py`.

### Exit Criteria

- Low-confidence queries trigger fallback or clarification instead of wrong routing.
- Policy rules block unauthorized access with clear reasons.
- Decision log captures full routing trace for every request.
- Test coverage > 80% for policy and fallback modules.

---

## Phase 3: Dashboard & Analytics (Weeks 5-6)

**Goal**: Dashboard with decision log and analytics, route management UI.

### Deliverables

- [x] **Next.js Dashboard**: Route registry viewer, decision log browser, confidence distribution chart.
- [x] **Route Management UI**: Create, edit, and delete routes from the dashboard. Sync with backend.
- [x] **Analytics**: Confidence score distributions, routing accuracy metrics, policy block frequency.
- [x] **API Client**: Typed TypeScript API client for all backend endpoints.
- [x] **Tests**: `test_integration.py` end-to-end test suite.

### Exit Criteria

- Dashboard displays real-time routing decisions from the API.
- Routes can be managed through the UI.
- Confidence chart visualizes distribution across all decisions.
- Full integration test suite passes.
