from collections.abc import AsyncIterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import db_session_dependency, get_routing_adapter
from app.main import app
from app.models import Base
from app.services.routing.models import RawRouteCandidate


class StubRoutingAdapter:
    async def plan_routes(self, payload: Any, redis_client: Any = None) -> tuple[list[RawRouteCandidate], list[str]]:
        return (
            [
                RawRouteCandidate(
                    mode="bike",
                    title="Bike Priority",
                    provider="stub",
                    distance_meters=8200,
                    base_duration_seconds=1560,
                    geometry={
                        "type": "LineString",
                        "coordinates": [
                            [payload.origin.lng, payload.origin.lat],
                            [payload.destination.lng, payload.destination.lat],
                        ],
                    },
                    raw_response={"stub": True},
                    comfort_score=0.8,
                ),
                RawRouteCandidate(
                    mode="rideshare",
                    title="Ride Share",
                    provider="stub",
                    distance_meters=8400,
                    base_duration_seconds=1320,
                    geometry={
                        "type": "LineString",
                        "coordinates": [
                            [payload.origin.lng, payload.origin.lat],
                            [payload.destination.lng, payload.destination.lat],
                        ],
                    },
                    raw_response={"stub": True},
                    comfort_score=0.82,
                ),
            ],
            [],
        )


@pytest.fixture
def client() -> TestClient:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_db() -> AsyncIterator[AsyncSession]:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[db_session_dependency] = override_db
    app.dependency_overrides[get_routing_adapter] = lambda: StubRoutingAdapter()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

