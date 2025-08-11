from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Transfer, TransferEvent
from ..notifications import broker


VALID_TRANSITIONS = {
    "INITIATED": ["PENDING", "FAILED"],
    "PENDING": ["COMPLETED", "FAILED"],
    "COMPLETED": [],
    "FAILED": [],
}


def advance_state(db: Session, transfer: Transfer, new_state: str):
    if new_state not in VALID_TRANSITIONS.get(transfer.status, []):
        # Allow idempotent re-sets
        if new_state != transfer.status:
            raise ValueError(f"Invalid state transition {transfer.status} -> {new_state}")
    transfer.status = new_state
    transfer.updated_at = datetime.utcnow()
    db.add(transfer)
    db.add(TransferEvent(transfer_id=transfer.id, type=new_state, payload={}))
    db.commit()
    # notify SSE subscribers
    from ..notifications import publish_event
    publish_event(transfer.id, {"type": new_state, "at": datetime.utcnow().isoformat()})