from typing import AsyncIterator

import httpx
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.services.dashboard_service import DashboardService
from app.services.intelligence.carbon import CarbonScoringEngine
from app.services.intelligence.recommendations import MobilityRecommendationEngine
from app.services.intelligence.scoring import RouteScoringEngine
from app.services.intelligence.traffic import TrafficScoreEstimator
from app.services.intelligence.travel_time import TravelTimePredictor
from app.services.mobility_service import MobilityPlanningService
from app.services.routing.graphhopper import GraphHopperRoutingAdapter
from app.services.routing.repository import TripRepository


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


def get_mobility_service(
    repository: TripRepository = Depends(get_trip_repository),
    routing_adapter: GraphHopperRoutingAdapter = Depends(get_routing_adapter),
    redis_client: Redis = Depends(get_redis_client),
) -> MobilityPlanningService:
    return MobilityPlanningService(
        repository=repository,
        routing_adapter=routing_adapter,
        redis_client=redis_client,
        traffic_estimator=TrafficScoreEstimator(),
        travel_time_predictor=TravelTimePredictor(),
        carbon_engine=CarbonScoringEngine(),
        scoring_engine=RouteScoringEngine(),
        recommendation_engine=MobilityRecommendationEngine(),
    )


def get_dashboard_service(
    repository: TripRepository = Depends(get_trip_repository),
) -> DashboardService:
    return DashboardService(repository=repository)

