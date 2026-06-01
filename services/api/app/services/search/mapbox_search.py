import uuid

import httpx

from app.core.config import get_settings
from app.schemas.common import GeoPoint
from app.schemas.search import SearchRetrieveResponse, SearchSuggestion, SearchSuggestResponse

settings = get_settings()


class MapboxSearchService:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self.http_client = http_client

    async def suggest(
        self,
        *,
        query: str,
        session_token: str | None,
        proximity: GeoPoint | None = None,
    ) -> SearchSuggestResponse:
        if not settings.mapbox_access_token:
            raise RuntimeError("Mapbox access token is not configured.")

        resolved_session_token = session_token or str(uuid.uuid4())
        params: dict[str, str] = {
            "q": query,
            "access_token": settings.mapbox_access_token,
            "session_token": resolved_session_token,
            "limit": "6",
            "types": "address,place,locality,poi",
        }
        if proximity:
            params["proximity"] = f"{proximity.lng},{proximity.lat}"

        response = await self.http_client.get(
            f"{settings.mapbox_search_base_url}/suggest",
            params=params,
        )
        response.raise_for_status()
        payload = response.json()

        suggestions = [
            SearchSuggestion(
                mapbox_id=item["mapbox_id"],
                name=item.get("name", item.get("name_preferred", "")),
                full_address=item.get("full_address", item.get("place_formatted", "")),
                feature_type=item.get("feature_type", "unknown"),
            )
            for item in payload.get("suggestions", [])
        ]
        return SearchSuggestResponse(session_token=resolved_session_token, suggestions=suggestions)

    async def retrieve(self, *, mapbox_id: str, session_token: str) -> SearchRetrieveResponse:
        if not settings.mapbox_access_token:
            raise RuntimeError("Mapbox access token is not configured.")

        response = await self.http_client.get(
            f"{settings.mapbox_search_base_url}/retrieve/{mapbox_id}",
            params={
                "access_token": settings.mapbox_access_token,
                "session_token": session_token,
            },
        )
        response.raise_for_status()
        features = response.json().get("features", [])
        if not features:
            raise RuntimeError("Mapbox returned no search feature.")
        feature = features[0]
        longitude, latitude = feature["geometry"]["coordinates"]
        return SearchRetrieveResponse(
            mapbox_id=feature["properties"]["mapbox_id"],
            label=feature["properties"].get("name", "Selected place"),
            address=feature["properties"].get("full_address", feature["properties"].get("place_formatted", "")),
            point=GeoPoint(lat=float(latitude), lng=float(longitude), label=feature["properties"].get("name")),
        )

    async def reverse(self, *, lat: float, lng: float) -> SearchRetrieveResponse:
        if not settings.mapbox_access_token:
            raise RuntimeError("Mapbox access token is not configured.")

        response = await self.http_client.get(
            f"{settings.mapbox_geocoding_base_url}/reverse",
            params={
                "longitude": lng,
                "latitude": lat,
                "access_token": settings.mapbox_access_token,
                "types": "address,street,place",
            },
        )
        response.raise_for_status()
        features = response.json().get("features", [])
        if not features:
            raise RuntimeError("Mapbox returned no reverse geocoding feature.")
        feature = features[0]
        longitude, latitude = feature["geometry"]["coordinates"]
        return SearchRetrieveResponse(
            mapbox_id=feature["properties"].get("mapbox_id", ""),
            label=feature["properties"].get("name", "Selected place"),
            address=feature["properties"].get("full_address", feature["properties"].get("place_formatted", "")),
            point=GeoPoint(lat=float(latitude), lng=float(longitude), label=feature["properties"].get("name")),
        )
