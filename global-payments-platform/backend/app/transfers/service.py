from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Transfer, TransferEvent, TransferStatus, Account
from app.transfers.iso20022.pacs008 import build_pacs008_xml, validate_pacs008
from app.utils.iban import validate_iban, validate_bic
from app.config import get_settings
from app.connectors.swift.adapter import SwiftConnector

settings = get_settings()

class TransferOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.swift = SwiftConnector(settings)

    async def create_transfer(self, debtor_account_id: int, creditor_iban: str, creditor_bic: str, amount, currency: str, reference: str | None, dry_run: bool):
        if not validate_iban(creditor_iban) or not validate_bic(creditor_bic):
            raise ValueError("Invalid IBAN/BIC")
        acct = await self.db.get(Account, debtor_account_id)
        if not acct:
            raise ValueError("Debtor account not found")
        xml = build_pacs008_xml(acct.iban, creditor_iban, creditor_bic, amount, currency, reference)
        ok, err = validate_pacs008(xml)
        if not ok:
            raise ValueError(f"pacs.008 invalid: {err}")
        transfer = Transfer(
            debtor_account_id=debtor_account_id,
            creditor_iban=creditor_iban,
            creditor_bic=creditor_bic,
            amount=amount,
            currency=currency,
            status=TransferStatus.INITIATED,
            reference=reference,
            pacs008_xml=xml,
        )
        self.db.add(transfer)
        await self.db.flush()
        await self._add_event(transfer.id, "INITIATED", None)
        if dry_run or settings.connector_swift_mode == "dry-run":
            transfer.status = TransferStatus.PENDING
            await self._add_event(transfer.id, "PENDING", "dry-run: validation-only")
            await self.db.commit()
            return transfer
        # live send
        try:
            resp = await self.swift.submit_pacs008(xml)
            transfer.status = TransferStatus.PENDING
            await self._add_event(transfer.id, "SUBMITTED", resp)
            await self.db.commit()
        except Exception as exc:
            transfer.status = TransferStatus.FAILED
            await self._add_event(transfer.id, "FAILED", str(exc))
            await self.db.commit()
        return transfer

    async def _add_event(self, transfer_id: int, type_: str, payload: str | None):
        evt = TransferEvent(transfer_id=transfer_id, type=type_, payload=payload)
        self.db.add(evt)