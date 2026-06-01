from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.cache import get_redis_ping
from app.core.config import get_settings

router = APIRouter()


@router.get("/liveness")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/readiness")
async def readiness() -> dict[str, str] | JSONResponse:
    settings = get_settings()
    redis_state = await get_redis_ping(settings.redis_url)
    status = "ready" if redis_state else "degraded"
    if not redis_state:
        return JSONResponse(status_code=503, content={"status": status})
    return {"status": status}
