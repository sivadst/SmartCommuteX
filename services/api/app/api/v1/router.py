from fastapi import APIRouter

from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.mobility import router as mobility_router
from app.api.v1.endpoints.realtime import router as realtime_router
from app.api.v1.endpoints.search import router as search_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
router.include_router(mobility_router, prefix="/mobility", tags=["mobility"])
router.include_router(realtime_router, prefix="/realtime", tags=["realtime"])
router.include_router(search_router, prefix="/search", tags=["search"])
