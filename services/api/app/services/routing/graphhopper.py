import hashlib
import json

import httpx
from redis.asyncio import Redis

from app.core.config import get_settings
from app.schemas.mobility import MobilityPlanRequest
from app.services.routing.models import RawRouteCandidate

settings = get_settings()


class GraphHopperRoutingAdapter:
    _mode_profile_map = {
        "walk": ("foot", "Pedestrian Corridor", 0.72),
        "bike": ("bike", "Bike Priority", 0.78),
        "ev": ("car", "EV Drive", 0.88),
        "rideshare": ("car", "Ride Share", 0.82),
    }

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self.http_client = http_client

    async def plan_routes(
        self, payload: MobilityPlanRequest, redis_client: Redis | None = None
    ) -> tuple[list[RawRouteCandidate], list[str]]:
        available: list[RawRouteCandidate] = []
        unavailable: list[str] = []

        if not settings.graphhopper_api_key:
            raise RuntimeError("GraphHopper API key is not configured.")

        for mode in payload.allowed_modes:
            profile_metadata = self._mode_profile_map.get(mode)
            if not profile_metadata:
                unavailable.append(mode)
                continue

            cache_key = self._cache_key(payload=payload, mode=mode)
            cached_payload = await self._read_cache(redis_client=redis_client, cache_key=cache_key)
            if cached_payload:
                available.append(self._deserialize_candidate(mode=mode, payload=cached_payload))
                continue

            profile, title, comfort_score = profile_metadata
            route = await self._fetch_route(profile=profile, payload=payload)
            candidate = RawRouteCandidate(
                mode=mode,
                title=title,
                provider="graphhopper",
                distance_meters=float(route["distance"]),
                base_duration_seconds=float(route["time"]) / 1000,
                geometry=route["points"],
                raw_response=route,
                comfort_score=comfort_score,
            )
            await self._write_cache(redis_client=redis_client, cache_key=cache_key, candidate=candidate)
            available.append(candidate)

        return available, unavailable

    async def _fetch_route(self, profile: str, payload: MobilityPlanRequest) -> dict[str, object]:
        request_body = {
            "profile": profile,
            "points": [
                [payload.origin.lng, payload.origin.lat],
                [payload.destination.lng, payload.destination.lat],
            ],
            "points_encoded": False,
            "instructions": False,
            "details": ["road_class", "surface", "road_environment"],
            "locale": "en",
        }

        response = await self.http_client.post(
            f"{settings.graphhopper_base_url}/route",
            params={"key": settings.graphhopper_api_key},
            json=request_body,
        )
        response.raise_for_status()
        body = response.json()

        paths = body.get("paths", [])
        if not paths:
            raise RuntimeError("GraphHopper returned no route candidates.")
        return paths[0]

    def _cache_key(self, payload: MobilityPlanRequest, mode: str) -> str:
        digest = hashlib.sha256(
            json.dumps(
                {
                    "mode": mode,
                    "origin": payload.origin.model_dump(),
                    "destination": payload.destination.model_dump(),
                    "departure": payload.departure_time.isoformat(),
                    "objective": payload.objective,
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        return f"smartcommutex:route:{digest}"

    async def _read_cache(self, redis_client: Redis | None, cache_key: str) -> dict[str, object] | None:
        if redis_client is None:
            return None

        try:
            payload = await redis_client.get(cache_key)
        except Exception:
            return None

        if payload is None:
            return None
        return json.loads(payload)

    async def _write_cache(
        self, redis_client: Redis | None, cache_key: str, candidate: RawRouteCandidate
    ) -> None:
        if redis_client is None:
            return

        try:
            await redis_client.set(
                cache_key,
                json.dumps(
                    {
                        "mode": candidate.mode,
                        "title": candidate.title,
                        "provider": candidate.provider,
                        "distance_meters": candidate.distance_meters,
                        "base_duration_seconds": candidate.base_duration_seconds,
                        "geometry": candidate.geometry,
                        "raw_response": candidate.raw_response,
                        "comfort_score": candidate.comfort_score,
                    }
                ),
                ex=settings.route_cache_ttl_seconds,
            )
        except Exception:
            return

    def _deserialize_candidate(self, mode: str, payload: dict[str, object]) -> RawRouteCandidate:
        return RawRouteCandidate(
            mode=mode,
            title=str(payload["title"]),
            provider=str(payload["provider"]),
            distance_meters=float(payload["distance_meters"]),
            base_duration_seconds=float(payload["base_duration_seconds"]),
            geometry=dict(payload["geometry"]),
            raw_response=dict(payload["raw_response"]),
            comfort_score=float(payload["comfort_score"]),
        )

