from pydantic import BaseModel, Field, constr
from typing import Optional, List
from decimal import Decimal
from app.models import TransferStatus

class AccountCreate(BaseModel):
    iban: str
    bic: str
    display_name: str

class AccountOut(BaseModel):
    id: int
    iban: str
    bic: str
    display_name: str

    class Config:
        from_attributes = True

class TransferCreate(BaseModel):
    debtor_account_id: int
    creditor_iban: str
    creditor_bic: str
    amount: Decimal = Field(gt=0)
    currency: constr(min_length=3, max_length=3)
    reference: Optional[str] = None
    dry_run: bool = True

class TransferOut(BaseModel):
    id: int
    status: TransferStatus
    reference: Optional[str]

    class Config:
        from_attributes = True

class TransferEventOut(BaseModel):
    id: int
    type: str
    payload: Optional[str]

    class Config:
        from_attributes = True

class KYCDocumentIn(BaseModel):
    document_type: str
    base64_content: str

class ValidateOut(BaseModel):
    valid: bool
    details: Optional[str] = None