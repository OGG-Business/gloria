from sqlalchemy.orm import Session
from ..models import Transfer
from ..core.config import settings


def send_transfer_via_mojaloop(db: Session, transfer: Transfer) -> None:
    if not settings.mojaloop_base_url:
        return
    import httpx

    payload = {
        "amount": str(transfer.amount),
        "currency": transfer.currency,
        "payer": {"idType": "IBAN", "idValue": transfer.debtor_account.iban},
        "payee": {"idType": "IBAN", "idValue": transfer.creditor_iban},
    }
    with httpx.Client(base_url=settings.mojaloop_base_url, timeout=10) as client:
        client.post("/transfers", json=payload)