from fastapi import APIRouter, Depends
from app.auth.security import require_roles

router = APIRouter()

@router.get("/status")
async def status(user=Depends(require_roles("admin", "operator"))):
    return {"ok": True}