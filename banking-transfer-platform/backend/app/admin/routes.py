from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def get_admin_info():
    return {"message": "Admin module", "endpoints": ["/dashboard", "/users", "/logs"]}
@router.get("/dashboard")
def admin_dashboard():
    return {"stats": {"users": 0, "transfers": 0, "accounts": 0}}
