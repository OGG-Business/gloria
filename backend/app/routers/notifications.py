from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()


async def event_stream():
    yield "event: ping\n\n"
    while True:
        await asyncio.sleep(10)
        yield "event: keepalive\n\n"


@router.get("/sse")
async def sse():
    return StreamingResponse(event_stream(), media_type="text/event-stream")