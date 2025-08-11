import base64
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import KYCDocument
from ..schemas import KYCDocumentIn
from ..security import get_current_user, encrypt_blob

router = APIRouter()


@router.post("/upload")
def upload_document(payload: KYCDocumentIn, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    try:
        data = base64.b64decode(payload.base64_content)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid base64 content") from exc
    encrypted = encrypt_blob(data)
    record = KYCDocument(user_id=user, doc_type=payload.doc_type, filename=payload.filename, encrypted_blob=encrypted)
    db.add(record)
    db.commit()
    return {"id": record.id}


@router.get("/")
def list_documents(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    docs = db.query(KYCDocument).filter(KYCDocument.user_id == user).all()
    return [{"id": d.id, "doc_type": d.doc_type, "filename": d.filename, "created_at": d.created_at} for d in docs]