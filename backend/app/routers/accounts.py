from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from ..auth import get_current_user
from ..services.iban import validate_iban, validate_bic, normalize_iban

router = APIRouter()


class Account(BaseModel):
    id: str
    owner_name: str
    iban: str = Field(..., description="International Bank Account Number")
    bic: str


_fake_accounts: List[Account] = []


@router.get("/me", response_model=List[Account])
def list_my_accounts(user=Depends(get_current_user)):
    return _fake_accounts


class AccountCreate(BaseModel):
    owner_name: str
    iban: str
    bic: str


@router.post("/", response_model=Account)
def create_account(payload: AccountCreate, user=Depends(get_current_user)):
    if not validate_iban(payload.iban):
        raise HTTPException(status_code=400, detail="Invalid IBAN")
    if not validate_bic(payload.bic):
        raise HTTPException(status_code=400, detail="Invalid BIC")
    acc = Account(id=f"acc_{len(_fake_accounts)+1}", owner_name=payload.owner_name, iban=normalize_iban(payload.iban) or payload.iban, bic=payload.bic)
    _fake_accounts.append(acc)
    return acc