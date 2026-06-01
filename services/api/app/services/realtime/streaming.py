import asyncio
from collections.abc import AsyncIterator

from fastapi import Request

from app.core.config import get_settings
from app.services.dashboard_service import DashboardService

settings = get_settings()


class CommandCenterStreamService:
    def __init__(self, dashboard_service: DashboardService) -> None:
        self.dashboard_service = dashboard_service

    async def stream(self, request: Request) -> AsyncIterator[str]:
        while True:
            if await request.is_disconnected():
                break
            snapshot = await self.dashboard_service.command_center_snapshot()
            yield f"event: city_pulse\ndata: {snapshot.model_dump_json()}\n\n"
            await asyncio.sleep(settings.realtime_stream_interval_seconds)
