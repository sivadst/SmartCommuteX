from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RawRouteCandidate:
    mode: str
    title: str
    provider: str
    route_variant: str
    path_index: int
    distance_meters: float
    base_duration_seconds: float
    geometry: dict[str, object]
    raw_response: dict[str, object]
    comfort_score: float
