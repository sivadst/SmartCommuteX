from fastapi import APIRouter, Depends

from app.api.deps import get_dashboard_service
from app.schemas.mobility import DashboardOverviewResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
async def dashboard_overview(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverviewResponse:
    return await service.overview()

