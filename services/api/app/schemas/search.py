from pydantic import BaseModel, Field

from app.schemas.common import GeoPoint


class SearchSuggestion(BaseModel):
    mapbox_id: str
    name: str
    full_address: str
    feature_type: str
    coordinates: GeoPoint | None = None


class SearchSuggestResponse(BaseModel):
    session_token: str
    suggestions: list[SearchSuggestion]


class SearchRetrieveResponse(BaseModel):
    mapbox_id: str
    label: str
    address: str
    point: GeoPoint

