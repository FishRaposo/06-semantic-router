# Architecture

## System Overview

SemanticRouter is a middleware layer that sits between a user (or agent) and a set of tools. It decides *which tool* to invoke based on the semantic content of the user's request, enforced by policies and confidence thresholds.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
│                                                                  │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │  Routes   │──▶│    Routing    │──▶│    Policy     │            │
│  │  API      │   │   Pipeline   │   │    Engine     │            │
│  └──────────┘   └──────────────┘   └──────┬───────┘            │
│                        │                      │                    │
│                  ┌─────▼──────┐        ┌─────▼──────┐           │
│                  │  Route      │        │  Fallback   │           │
│                  │  Registry   │        │  Handler    │           │
│                  └─────┬──────┘        └────────────┘           │
│                        │                                          │
│                  ┌─────▼──────┐   ┌──────────────┐              │
│                  │  Embedding  │   │  Execution   │              │
│                  │  Service    │   │  Adapter     │              │
│                  └────────────┘   └──────┬───────┘              │
│                                          │                       │
│                                    ┌─────▼──────┐              │
│                                    │  Mock/Real  │              │
│                                    │  Tools      │              │
│                                    └────────────┘              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL + pgvector                        │  │
│  │    (Routes, Decisions, Embeddings)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Request arrives** at `POST /api/v1/route` with a query, optional context, and user metadata.
2. **Route Registry** provides candidate routes with pre-computed embeddings.
3. **Embedding Service** embeds the query.
4. **Semantic Matcher** computes cosine similarity between query embedding and each route's embedding.
5. **Route Selector** picks the best match, applying confidence thresholds.
6. **Policy Engine** evaluates permissions and rules against the selected route and user context.
7. **Fallback Handler** intervenes if confidence is low or policy blocks the route.
8. **Execution Adapter** dispatches to the appropriate tool.
9. **Decision Log** records the entire decision trace.

## Embedding Strategy

- Route descriptions are embedded once at registration time and cached.
- User queries are embedded at request time.
- Supports both OpenAI (`text-embedding-3-small`) and sentence-transformers (`all-MiniLM-L6-v2`).
- Embeddings are stored in PostgreSQL with pgvector for similarity search at scale.

## State Management

- **Stateless routing**: Each request is processed independently.
- **Decision log**: Persisted to PostgreSQL for analytics and debugging.
- **Route registry**: Loaded from YAML at startup, optionally refreshed from DB.
- **Embedding cache**: In-memory LRU cache with optional DB persistence.

## Deployment

- **API**: Docker container running Uvicorn with FastAPI.
- **Dashboard**: Docker container running Next.js.
- **Database**: PostgreSQL 16 with pgvector extension.
- All orchestrated via `docker-compose.yml`.
