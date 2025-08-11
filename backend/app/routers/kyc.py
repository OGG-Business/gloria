from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from ..auth import get_current_user
from ..services.crypto import encrypt

router = APIRouter()

_kyc_storage: dict[str, bytes] = {}


@router.post("/documents")
async def upload_document(doc_type: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    encrypted = encrypt(content)
    key = f"{user.get('sub')}_{doc_type}_{file.filename}"
    _kyc_storage[key] = encrypted
    return {"status": "stored", "key": key}