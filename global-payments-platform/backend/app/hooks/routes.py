from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/sanctions/callback")
async def sanctions_callback(req: Request):
    body = await req.json()
    return {"status": "received"}