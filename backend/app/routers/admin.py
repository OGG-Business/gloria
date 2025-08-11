from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import AuditLog, Transfer
from ..security import get_current_user

router = APIRouter()


@router.get("/logs")
def get_logs(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": l.id,
            "trace_id": l.trace_id,
            "actor": l.actor,
            "action": l.action,
            "entity": l.entity,
            "entity_id": l.entity_id,
            "created_at": l.created_at,
        }
        for l in logs
    ]


@router.post("/reprocess/{transfer_id}")
def reprocess_transfer(transfer_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    transfer = db.query(Transfer).get(transfer_id)
    if not transfer:
        return {"status": "not_found"}
    # In production: re-enqueue processing
    return {"status": "enqueued"}