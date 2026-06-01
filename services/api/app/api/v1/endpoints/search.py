from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_search_service
from app.schemas.common import GeoPoint
from app.schemas.search import SearchRetrieveResponse, SearchSuggestResponse
from app.services.search.mapbox_search import MapboxSearchService

router = APIRouter()


@router.get("/suggest", response_model=SearchSuggestResponse)
async def suggest_locations(
    q: str = Query(min_length=2),
    session_token: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    service: MapboxSearchService = Depends(get_search_service),
) -> SearchSuggestResponse:
    try:
        proximity = GeoPoint(lat=lat, lng=lng) if lat is not None and lng is not None else None
        return await service.suggest(query=q, session_token=session_token, proximity=proximity)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/retrieve/{mapbox_id}", response_model=SearchRetrieveResponse)
async def retrieve_location(
    mapbox_id: str,
    session_token: str,
    service: MapboxSearchService = Depends(get_search_service),
) -> SearchRetrieveResponse:
    try:
        return await service.retrieve(mapbox_id=mapbox_id, session_token=session_token)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/reverse", response_model=SearchRetrieveResponse)
async def reverse_geocode(
    lat: float,
    lng: float,
    service: MapboxSearchService = Depends(get_search_service),
) -> SearchRetrieveResponse:
    try:
        return await service.reverse(lat=lat, lng=lng)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
