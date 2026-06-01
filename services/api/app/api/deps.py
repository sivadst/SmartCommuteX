from typing import AsyncIterator

import httpx
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.services.dashboard_service import DashboardService
from app.services.intelligence.providers import (
    HeuristicAnomalyDetectionProvider,
    HeuristicCarbonEstimator,
    HeuristicCongestionProvider,
    HeuristicETAProvider,
    HeuristicRouteRefreshPolicy,
    ModelProviderSuite,
    OpenMeteoWeatherPenaltyProvider,
    RepositoryHabitLearningProvider,
    RuleBasedRecommendationProvider,
)
from app.services.mobility_service import MobilityPlanningService
from app.services.realtime.streaming import CommandCenterStreamService
from app.services.routing.graphhopper import GraphHopperRoutingAdapter
from app.services.routing.repository import TripRepository
from app.services.search.mapbox_search import MapboxSearchService


async def db_session_dependency() -> AsyncIterator[AsyncSession]:
    async for session in get_db_session():
        yield session


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis


def get_trip_repository(session: AsyncSession = Depends(db_session_dependency)) -> TripRepository:
    return TripRepository(session=session)


def get_routing_adapter(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> GraphHopperRoutingAdapter:
    return GraphHopperRoutingAdapter(http_client=client)


def get_search_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> MapboxSearchService:
    return MapboxSearchService(http_client=client)


def get_model_provider_suite(
    repository: TripRepository = Depends(get_trip_repository),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ModelProviderSuite:
    return ModelProviderSuite(
        eta=HeuristicETAProvider(),
        congestion=HeuristicCongestionProvider(),
        carbon=HeuristicCarbonEstimator(),
        weather=OpenMeteoWeatherPenaltyProvider(http_client=client),
        habits=RepositoryHabitLearningProvider(repository=repository),
        anomaly=HeuristicAnomalyDetectionProvider(),
        recommendation=RuleBasedRecommendationProvider(),
        refresh_policy=HeuristicRouteRefreshPolicy(),
    )


def get_mobility_service(
    repository: TripRepository = Depends(get_trip_repository),
    routing_adapter: GraphHopperRoutingAdapter = Depends(get_routing_adapter),
    redis_client: Redis = Depends(get_redis_client),
    model_suite: ModelProviderSuite = Depends(get_model_provider_suite),
) -> MobilityPlanningService:
    return MobilityPlanningService(
        repository=repository,
        routing_adapter=routing_adapter,
        redis_client=redis_client,
        model_suite=model_suite,
    )


def get_dashboard_service(
    repository: TripRepository = Depends(get_trip_repository),
) -> DashboardService:
    return DashboardService(repository=repository)


def get_command_center_stream_service(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> CommandCenterStreamService:
    return CommandCenterStreamService(dashboard_service=dashboard_service)
