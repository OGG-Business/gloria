from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.schemas import TransferCreate, TransferOut, TransferEventOut, ValidateOut
from app.models import Transfer, TransferEvent
from app.transfers.service import TransferOrchestrator
from app.transfers.iso20022.pacs008 import validate_pacs008
from app.auth.security import get_current_user

router = APIRouter()

@router.post("/", response_model=TransferOut)
async def create_transfer(payload: TransferCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    orch = TransferOrchestrator(db)
    try:
        tr = await orch.create_transfer(
            debtor_account_id=payload.debtor_account_id,
            creditor_iban=payload.creditor_iban,
            creditor_bic=payload.creditor_bic,
            amount=payload.amount,
            currency=payload.currency,
            reference=payload.reference,
            dry_run=payload.dry_run,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return tr

@router.get("/", response_model=list[TransferOut])
async def list_transfers(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Transfer))
    return res.scalars().all()

@router.get("/{transfer_id}/events", response_model=list[TransferEventOut])
async def transfer_events(transfer_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(TransferEvent).where(TransferEvent.transfer_id == transfer_id))
    return res.scalars().all()

@router.post("/validate", response_model=ValidateOut)
async def validate(xml: str, user=Depends(get_current_user)):
    ok, err = validate_pacs008(xml)
    return {"valid": ok, "details": err}