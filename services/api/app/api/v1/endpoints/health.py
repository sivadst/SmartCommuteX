from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.db import check_database_connection
from app.core.cache import get_redis_ping
from app.core.config import get_settings

router = APIRouter()


@router.get("/liveness")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/readiness", response_model=None)
async def readiness():
    settings = get_settings()
    redis_state = await get_redis_ping(settings.redis_url)
    database_state = await check_database_connection()
    status = "ready" if redis_state and database_state else "degraded"
    payload = {"status": status, "redis": redis_state, "database": database_state}
    if status != "ready":
        return JSONResponse(status_code=503, content=payload)
    return payload
