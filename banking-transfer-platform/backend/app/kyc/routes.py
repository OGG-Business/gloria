from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def get_kyc_info():
    return {"message": "KYC module", "endpoints": ["/upload", "/verify", "/status"]}
@router.post("/upload")
def upload_document():
    return {"message": "Document uploaded", "status": "processing"}
