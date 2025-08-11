from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, constr


class AccountCreate(BaseModel):
    user_id: str
    name: str
    iban: constr(strip_whitespace=True)
    bic: Optional[str] = None


class AccountOut(BaseModel):
    id: int
    user_id: str
    name: str
    iban: str
    bic: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    debtor_account_id: int
    creditor_name: str
    creditor_iban: str
    creditor_bic: Optional[str] = None
    amount: float
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    metadata: Dict[str, Any] = {}


class TransferOut(BaseModel):
    id: int
    status: str
    amount: float
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransferEventOut(BaseModel):
    id: int
    transfer_id: int
    type: str
    payload: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class KYCDocumentIn(BaseModel):
    doc_type: str
    filename: str
    base64_content: str


class HealthOut(BaseModel):
    status: str
    environment: str