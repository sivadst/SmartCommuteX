from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_mobility_service
from app.schemas.mobility import MobilityPlanRequest, MobilityPlanResponse
from app.services.mobility_service import MobilityPlanningService

router = APIRouter()


@router.post("/plan", response_model=MobilityPlanResponse)
async def plan_commute(
    payload: MobilityPlanRequest,
    service: MobilityPlanningService = Depends(get_mobility_service),
) -> MobilityPlanResponse:
    try:
        return await service.plan(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

