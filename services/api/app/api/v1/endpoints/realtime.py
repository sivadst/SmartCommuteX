from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.deps import get_command_center_stream_service
from app.services.realtime.streaming import CommandCenterStreamService

router = APIRouter()


@router.get("/command-center")
async def command_center_stream(
    request: Request,
    service: CommandCenterStreamService = Depends(get_command_center_stream_service),
) -> StreamingResponse:
    return StreamingResponse(
        service.stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
