from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import KYCDocument
from app.utils.crypto import crypto_manager
from app.auth.security import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_kyc(document_type: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    data = await file.read()
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    cipher = crypto_manager.encrypt(data)
    rec = KYCDocument(user_id=0, document_type=document_type, encrypted_blob=cipher)
    db.add(rec)
    await db.commit()
    return {"status": "stored"}