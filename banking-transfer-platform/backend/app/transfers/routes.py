from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def get_transfers():
    return {"message": "Transfers module", "endpoints": ["/create", "/list", "/status"]}
@router.post("/create")
def create_transfer():
    return {"message": "Transfer created", "status": "pending"}
