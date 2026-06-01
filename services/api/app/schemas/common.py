from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    label: str | None = Field(default=None, max_length=120)


class LineStringGeometry(BaseModel):
    type: str = "LineString"
    coordinates: list[list[float]]
