from collections.abc import AsyncIterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import db_session_dependency, get_model_provider_suite, get_routing_adapter
from app.main import app
from app.models import Base
from app.services.intelligence.interfaces import (
    AnomalySignal,
    CongestionForecast,
    ETAForecast,
    WeatherImpact,
)
from app.services.intelligence.providers import (
    HeuristicCarbonEstimator,
    HeuristicRouteRefreshPolicy,
    ModelProviderSuite,
    RuleBasedRecommendationProvider,
)
from app.services.routing.models import RawRouteCandidate


class StubRoutingAdapter:
    async def plan_routes(self, payload: Any, redis_client: Any = None) -> tuple[list[RawRouteCandidate], list[str]]:
        return (
            [
                RawRouteCandidate(
                    mode="bike",
                    title="Bike Priority",
                    provider="stub",
                    route_variant="primary",
                    path_index=0,
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
                    route_variant="alternative_1",
                    path_index=1,
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


class StubCongestionProvider:
    def forecast(self, *, mode: str, departure_time: Any, distance_meters: float) -> CongestionForecast:
        return CongestionForecast(score=34.0 if mode == "bike" else 58.0, summary="Stub congestion.")


class StubETAProvider:
    def predict_duration_seconds(
        self, *, base_duration_seconds: float, traffic_score: float, mode: str
    ) -> ETAForecast:
        multiplier = 1.04 if mode == "bike" else 1.18
        reliability = 0.86 if mode == "bike" else 0.68
        return ETAForecast(
            predicted_duration_seconds=round(base_duration_seconds * multiplier, 2),
            reliability_score=reliability,
        )


class StubWeatherProvider:
    async def get_penalty(self, *, lat: float, lng: float, departure_time: Any, mode: str) -> WeatherImpact:
        return WeatherImpact(penalty=0.02 if mode == "bike" else 0.05, summary="Stub weather.")


class StubHabitProvider:
    async def get_affinity(self, *, origin_label: str, destination_label: str, mode: str) -> float:
        return 0.74 if mode == "bike" else 0.52


class StubAnomalyProvider:
    def assess(
        self,
        *,
        traffic_score: float,
        base_duration_seconds: float,
        predicted_duration_seconds: float,
        weather_penalty: float,
    ) -> AnomalySignal:
        return AnomalySignal(severity=0.18 if traffic_score < 40 else 0.34, summary="Stub anomaly.")


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
    app.dependency_overrides[get_model_provider_suite] = lambda: ModelProviderSuite(
        eta=StubETAProvider(),
        congestion=StubCongestionProvider(),
        carbon=HeuristicCarbonEstimator(),
        weather=StubWeatherProvider(),
        habits=StubHabitProvider(),
        anomaly=StubAnomalyProvider(),
        recommendation=RuleBasedRecommendationProvider(),
        refresh_policy=HeuristicRouteRefreshPolicy(),
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
