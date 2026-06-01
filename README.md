# SmartCommuteX

SmartCommuteX is an AI mobility operating system for carbon-aware, multimodal commute intelligence. This repository now starts from a production-grade foundation instead of a demo scaffold: a premium Next.js frontend, an async-first FastAPI service layer, Redis/Celery operational primitives, and deployment-ready local infrastructure.

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

- Cinematic mobility-tech landing experience with reusable UI primitives and state/query providers.
- Backend health/readiness endpoints and a typed commute recommendation API.
- Dockerized web, API, worker, PostgreSQL, and Redis services.
- Monorepo workspace ready for analytics, routing, auth, ML pipelines, and observability.

## Near-Term Build Path

1. Integrate Mapbox and route rendering with GraphHopper-backed trip graph queries.
2. Add PostgreSQL persistence and Redis-backed route/result caching.
3. Introduce ML feature pipelines for traffic prediction, carbon modeling, and personalized route ranking.
4. Stand up auth, rate limiting, and event telemetry for production operations.

## Standards

Every layer should optimize for scalability, maintainability, performance, UX polish, and production safety. If a change does not improve those dimensions, it should not land.

