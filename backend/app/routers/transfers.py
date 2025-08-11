import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Transfer, TransferEvent, Account
from ..schemas import TransferCreate, TransferOut, TransferEventOut
from ..security import get_current_user
from ..core.config import settings
from ..notifications import broker
from ..services.state import advance_state
from ..connectors.swift import send_pacs008_via_swift
from ..connectors.mojaloop import send_transfer_via_mojaloop

router = APIRouter()


@router.post("/", response_model=TransferOut)
def create_transfer(payload: TransferCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    debtor = db.query(Account).get(payload.debtor_account_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="Debtor account not found")
    from ..services.compliance import validate_transfer_rules
    try:
        validate_transfer_rules(payload.creditor_name, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    transfer = Transfer(
        debtor_account_id=payload.debtor_account_id,
        creditor_name=payload.creditor_name,
        creditor_iban=payload.creditor_iban.replace(" ", ""),
        creditor_bic=payload.creditor_bic,
        amount=payload.amount,
        currency=payload.currency,
        status="INITIATED",
        metadata=payload.metadata or {},
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)

    _persist_event(db, transfer.id, "INITIATED", {"at": datetime.utcnow().isoformat()})
    advance_state(db, transfer, "PENDING")

    if settings.dry_run or settings.bank_approval.lower() != "yes":
        _persist_event(db, transfer.id, "COMPLETED", {"dry_run": True})
        advance_state(db, transfer, "COMPLETED")
    else:
        # Dispatch to connectors based on configuration
        if settings.swift_mode != "dry":
            send_pacs008_via_swift(db, transfer)
        elif settings.mojaloop_base_url:
            send_transfer_via_mojaloop(db, transfer)
        else:
            _persist_event(db, transfer.id, "FAILED", {"reason": "No connector configured"})
            advance_state(db, transfer, "FAILED")

    return transfer


def _persist_event(db: Session, transfer_id: int, event_type: str, payload: dict):
    event = TransferEvent(transfer_id=transfer_id, type=event_type, payload=payload)
    db.add(event)
    db.commit()


@router.get("/{transfer_id}", response_model=TransferOut)
def get_transfer(transfer_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    transfer = db.query(Transfer).get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Not found")
    return transfer


@router.get("/{transfer_id}/events", response_model=list[TransferEventOut])
def list_events(transfer_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return db.query(TransferEvent).filter(TransferEvent.transfer_id == transfer_id).order_by(TransferEvent.created_at).all()


@router.get("/{transfer_id}/events/stream")
async def stream_events(transfer_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    async def event_generator():
        async for event in broker.subscribe(transfer_id):
            yield f"data: {json.dumps(event)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")