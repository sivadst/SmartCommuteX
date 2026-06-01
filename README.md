# SmartCommuteX

SmartCommuteX is an AI mobility operating system for carbon-aware, multimodal commute intelligence. The repository now includes a real map-first product slice: GraphHopper-powered route planning, an interactive Mapbox trip canvas, persisted trip intelligence, and dashboard analytics on top of the original production-grade foundation.

## Platform Shape

- `apps/web`: Next.js App Router frontend with TypeScript, TailwindCSS, Framer Motion, Zustand, and React Query.
- `services/api`: FastAPI backend with versioned APIs, typed schemas, structured logging, readiness endpoints, and recommendation services.
- `docs/architecture.md`: system architecture, service boundaries, data flow, and scale path.
- `.github/workflows/ci.yml`: CI baseline for frontend and backend quality gates.

## Quick Start

1. Copy `.env.example` to `.env`.
2. Start infrastructure with `docker compose up --build`.
3. Open `http://localhost:3000` for the frontend and `http://localhost:8000/api/v1/health/liveness` for the API.

## What Exists Today

- Premium map-centric Next.js experience with live route comparison, dynamic markers, and animated overlays.
- FastAPI route planning pipeline with GraphHopper integration, traffic/time/carbon intelligence, and ranking logic.
- Async SQLAlchemy models plus Alembic migrations for users, trips, route snapshots, saved routes, carbon metrics, and commute profiles.
- Dashboard analytics surface backed by persisted trip and sustainability data.
- Dockerized web, API, worker, PostgreSQL, and Redis services.

## Required Environment

- `NEXT_PUBLIC_MAPBOX_TOKEN`: required for the live map canvas.
- `GRAPHHOPPER_API_KEY`: required for real route generation.
- `docker compose up --build`: runs Alembic migrations automatically before API and worker startup.

## Near-Term Build Path

1. Add route alternative expansion, EV charging heuristics, and transit adapters.
2. Introduce geocoding/search, user auth, and saved-route workflows in the UI.
3. Move baseline intelligence services behind dedicated model-serving interfaces for ML upgrades.
4. Add observability, rate limiting, and event telemetry for production operations.

## Standards

Every layer should optimize for scalability, maintainability, performance, UX polish, and production safety. If a change does not improve those dimensions, it should not land.
