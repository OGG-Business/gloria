from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def get_accounts():
    return {"message": "Accounts module", "endpoints": ["/list", "/create", "/balance"]}
@router.get("/list")
def list_accounts():
    return {"accounts": [], "total": 0}
