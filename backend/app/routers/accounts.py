from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from stdnum import iban as stdnum_iban
from stdnum import bic as stdnum_bic
from ..db import get_db
from ..models import Account
from ..schemas import AccountCreate, AccountOut
from ..security import get_current_user
from ..audit import write_audit_log

router = APIRouter()


@router.post("/", response_model=AccountOut)
def create_account(payload: AccountCreate, request: Request, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    try:
        stdnum_iban.validate(payload.iban)
        if payload.bic:
            stdnum_bic.validate(payload.bic)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid IBAN/BIC: {exc}") from exc
    account = Account(user_id=payload.user_id, name=payload.name, iban=payload.iban.replace(" ", ""), bic=payload.bic)
    db.add(account)
    db.commit()
    db.refresh(account)
    write_audit_log(db, getattr(request.state, "trace_id", "-"), user, "CREATE", "Account", str(account.id), {"iban": account.iban})
    return account


@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return db.query(Account).all()