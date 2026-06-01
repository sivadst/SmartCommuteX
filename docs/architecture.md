# SmartCommuteX Architecture

## North Star

SmartCommuteX is designed as a mobility intelligence platform, not a single-purpose route form. The system is structured to support multimodal routing, predictive travel-time estimation, carbon scoring, personalization, and eventually smart-city data products.

## Monorepo Boundaries

- `apps/web`
  - Presentation layer
  - Query orchestration
  - Local interaction state
  - Map and trip-exploration UI
- `services/api`
  - External API surface
  - Domain orchestration
  - Validation and policy enforcement
  - Background task handoff
- `data/` future
  - Feature definitions
  - Offline training pipelines
  - Model artifacts
- `infra/` future
  - Terraform
  - Helm or container deployment manifests
  - Environment overlays

## Backend Service Architecture

The API is intentionally split into:

- `core`
  - Settings
  - logging
  - dependency wiring
  - cache/database adapters
- `api/v1`
  - Stable versioned HTTP surface
- `schemas`
  - Request and response contracts
- `services`
  - Business orchestration and scoring logic
- `workers`
  - Celery background execution

This keeps transport, domain logic, and infrastructure cleanly separated and makes future extraction into dedicated microservices straightforward.

## Frontend Architecture

The frontend uses the App Router with thin route files and reusable component primitives. State is split intentionally:

- React Query
  - server state
  - caching
  - request lifecycle
- Zustand
  - local exploration state
  - selected commute preferences
  - UI panel coordination

The visual system is tokenized in CSS variables to support future theming across consumer and enterprise surfaces.

## Request Flow

1. User defines origin, destination, and preference weights in the frontend.
2. Frontend submits a typed request to `/api/v1/mobility/plan`.
3. API validates payloads and calls the mobility planning service.
4. Mobility planning service:
   - fetches per-mode route geometry from GraphHopper
   - applies Redis route caching
   - estimates traffic pressure
   - predicts travel time uplift
   - computes carbon and cost metrics
   - ranks routes by objective
   - persists trip and route snapshots in PostgreSQL
5. Dashboard reads persisted data from `/api/v1/dashboard/overview`.

## Scale Path

- Phase 1
  - Monolith with strong boundaries
  - PostgreSQL + Redis
  - Celery for async jobs
- Phase 2
  - Dedicated routing, inference, and analytics services
  - event streaming for telemetry
  - feature store and model registry
- Phase 3
  - city-scale partner APIs
  - digital twin analytics
  - B2B mobility intelligence products

## Operational Standards

- Typed contracts everywhere
- Strict environment-based configuration
- Readiness and liveness probes
- Structured logs
- Rate limiting and auth hooks
- Cache-first external route enrichment
- Background execution for heavy optimization and model inference
- Alembic-managed schema evolution
- Map-first UX with API-backed analytics surfaces
