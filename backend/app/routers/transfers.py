from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List
from enum import Enum
from ..auth import get_current_user
from ..services.iban import validate_iban, validate_bic
from ..services.audit import append_audit
from ..services.iso20022 import build_pacs008, map_to_mt103
from ..config import settings
from ..services.connectors.swift import SwiftConnector
from ..services.connectors.mojaloop import MojaloopConnector

router = APIRouter()


class TransferState(str, Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TransferCreate(BaseModel):
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    debtor_iban: str
    debtor_bic: str
    creditor_iban: str
    creditor_bic: str
    remittance_info: str | None = None
    channel: str | None = Field(default="swift", description="swift|mojaloop")


class Transfer(BaseModel):
    id: str
    state: TransferState
    events: List[Dict]


_transfers: Dict[str, Transfer] = {}


def _send_async(transfer: Transfer, payload: Dict):
    # choose connector
    channel = payload.get("channel") or "swift"
    connector_resp = {"status": "DRY_RUN"}
    if channel == "swift" and settings.swift_base_url:
        connector = SwiftConnector(settings.swift_base_url, settings.swift_client_cert, settings.swift_client_key, settings.swift_ca_cert)
        # In background task sync call (no await)
        import anyio
        async def _do():
            nonlocal connector_resp
            connector_resp = await connector.send_credit_transfer(payload, dry_run=settings.dry_run)
        anyio.run(_do)
    elif channel == "mojaloop" and settings.mojaloop_base_url:
        connector = MojaloopConnector(settings.mojaloop_base_url)
        import anyio
        async def _do2():
            nonlocal connector_resp
            connector_resp = await connector.send_credit_transfer(payload, dry_run=settings.dry_run)
        anyio.run(_do2)
    # update events
    transfer.events.append({"type": "CONNECTOR_RESPONSE", "data": connector_resp})
    if connector_resp.get("status") in (200, "ACK", "DRY_RUN"):
        transfer.state = TransferState.PENDING if not settings.dry_run else TransferState.COMPLETED
        transfer.events.append({"type": "STATE_CHANGED", "to": transfer.state})
    else:
        transfer.state = TransferState.FAILED
        transfer.events.append({"type": "STATE_CHANGED", "to": transfer.state})


@router.post("/", response_model=Transfer)
def create_transfer(payload: TransferCreate, background: BackgroundTasks, user=Depends(get_current_user)):
    if payload.amount > settings.block_threshold_usd and payload.currency.upper() == "USD":
        raise HTTPException(status_code=403, detail="Amount exceeds policy threshold")
    if not validate_iban(payload.debtor_iban) or not validate_iban(payload.creditor_iban):
        raise HTTPException(status_code=400, detail="Invalid IBAN")
    if not validate_bic(payload.debtor_bic) or not validate_bic(payload.creditor_bic):
        raise HTTPException(status_code=400, detail="Invalid BIC")
    tid = f"tr_{len(_transfers)+1}"
    events = [{"type": "STATE_CHANGED", "to": "INITIATED"}]
    t = Transfer(id=tid, state=TransferState.INITIATED, events=events)
    _transfers[tid] = t

    iso_xml = build_pacs008({
        "id": tid,
        "amount": payload.amount,
        "currency": payload.currency,
        "debtor_iban": payload.debtor_iban,
        "creditor_iban": payload.creditor_iban,
        "remittance_info": payload.remittance_info or ""
    })
    mt103 = map_to_mt103({
        "id": tid,
        "amount": payload.amount,
        "currency": payload.currency,
        "debtor_iban": payload.debtor_iban,
        "creditor_iban": payload.creditor_iban,
        "remittance_info": payload.remittance_info or ""
    })
    t.events.append({"type": "ISO20022", "format": "pacs.008", "xml": iso_xml})
    t.events.append({"type": "SWIFT_MT", "format": "MT103", "message": mt103})

    append_audit("TRANSFER_CREATED", tid, user.get("sub", "unknown"), payload.model_dump())

    background.add_task(_send_async, t, {**payload.model_dump(), "id": tid})

    return t


@router.get("/{transfer_id}", response_model=Transfer)
def get_transfer(transfer_id: str, user=Depends(get_current_user)):
    t = _transfers.get(transfer_id)
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    return t


@router.get("/{transfer_id}/events", response_model=List[Dict])
def get_transfer_events(transfer_id: str, user=Depends(get_current_user)):
    t = _transfers.get(transfer_id)
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    return t.events