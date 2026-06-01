from fastapi import APIRouter

from app.schemas.mobility import CommuteRecommendationRequest, CommuteRecommendationResponse
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()
engine = RecommendationEngine()


@router.post("/recommendations", response_model=CommuteRecommendationResponse)
async def get_recommendations(
    payload: CommuteRecommendationRequest,
) -> CommuteRecommendationResponse:
    return engine.rank_commute_options(payload)

