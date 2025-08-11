from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import asyncio

router = APIRouter()

async def event_generator():
    while True:
        yield {"event": "keepalive", "data": "ok"}
        await asyncio.sleep(5)

@router.get("/stream")
async def stream():
    return EventSourceResponse(event_generator())