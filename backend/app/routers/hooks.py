from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/swift")
async def swift_hook(request: Request):
    payload = await request.json()
    # TODO: verify signatures/mTLS source, update transfer status
    return {"received": True}


@router.post("/mojaloop")
async def mojaloop_hook(request: Request):
    payload = await request.json()
    return {"received": True}