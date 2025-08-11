from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/swift/callback")
async def swift_callback(request: Request):
    payload = await request.json()
    # In production, verify signature / mTLS
    return {"status": "received", "payload": payload}