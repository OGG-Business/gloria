from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.schemas import AccountCreate, AccountOut
from app.models import Account
from app.utils.iban import validate_iban, validate_bic
from app.utils.crypto import crypto_manager
from app.auth.security import get_current_user

router = APIRouter()

@router.post("/", response_model=AccountOut)
async def create_account(payload: AccountCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if not validate_iban(payload.iban):
        raise HTTPException(status_code=400, detail="Invalid IBAN")
    if not validate_bic(payload.bic):
        raise HTTPException(status_code=400, detail="Invalid BIC")
    encrypted = crypto_manager.encrypt(f"owner={user['sub']}".encode())
    acct = Account(user_id=0, iban=payload.iban, bic=payload.bic, display_name=payload.display_name, sensitive_metadata=encrypted)
    db.add(acct)
    await db.commit()
    await db.refresh(acct)
    return acct

@router.get("/", response_model=list[AccountOut])
async def list_accounts(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    res = await db.execute(select(Account))
    rows = res.scalars().all()
    return rows