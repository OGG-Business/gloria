from fastapi import APIRouter, Depends
from app.auth.security import get_current_user

router = APIRouter()

@router.get("/me")
async def me(user = Depends(get_current_user)):
    return user