from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Transfer, TransferEvent, TransferStatus, Account
from app.utils.iban import validate_iban, validate_bic
from app.config import get_settings
from app.connectors.azqore_connector import AzqoreConnector
import json

settings = get_settings()

class TransferOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Use the new Azqore connector
        self.azqore = AzqoreConnector(settings)

    async def create_transfer(self, debtor_account_id: int, creditor_iban: str, creditor_bic: str, amount: float, currency: str, reference: str | None, dry_run: bool):
        if not validate_iban(creditor_iban) or not validate_bic(creditor_bic):
            raise ValueError("Invalid IBAN/BIC")

        acct = await self.db.get(Account, debtor_account_id)
        if not acct:
            raise ValueError("Debtor account not found")

        # Create the initial transfer record
        transfer = Transfer(
            debtor_account_id=debtor_account_id,
            creditor_iban=creditor_iban,
            creditor_bic=creditor_bic,
            amount=amount,
            currency=currency,
            status=TransferStatus.INITIATED,
            reference=reference,
        )
        self.db.add(transfer)
        await self.db.flush()
        await self._add_event(transfer.id, "INITIATED", "Transfer initiated by user.")

        if dry_run:
            transfer.status = TransferStatus.COMPLETED # In dry-run, we simulate completion
            await self._add_event(transfer.id, "COMPLETED", "Dry-run mode: transfer simulated.")
            await self.db.commit()
            return transfer

        # --- Live Mode: 3-step AZQORE Workflow ---
        try:
            # Step 1: Get Quotation
            quotation = await self.azqore.get_quotation(amount, currency, creditor_bic)
            quotation_id = quotation.get("id")
            transfer.quotation_id = quotation_id
            await self._add_event(transfer.id, "QUOTED", f"Quotation received: {quotation_id}")

            # Step 2: Create Transaction
            beneficiary_details = {"name": "Beneficiary Name", "address": "Beneficiary Address"} # Placeholder
            transaction = await self.azqore.create_transaction(quotation_id, beneficiary_details)
            transaction_id = transaction.get("id")
            transfer.transaction_id = transaction_id
            transfer.status = TransferStatus.PENDING
            await self._add_event(transfer.id, "TRANSACTION_CREATED", f"Transaction created: {transaction_id}")

            # Step 3: Confirm Transaction
            confirmation = await self.azqore.confirm_transaction(transaction_id)
            await self._add_event(transfer.id, "CONFIRMED", f"Transaction confirmed by API: {confirmation.get('status')}")

            # Final status is pending, waiting for callback or polling to confirm completion
            await self.db.commit()

        except Exception as exc:
            transfer.status = TransferStatus.FAILED
            await self._add_event(transfer.id, "FAILED", str(exc))
            await self.db.commit()

        return transfer

    async def _add_event(self, transfer_id: int, type_: str, payload: str | None):
        evt = TransferEvent(transfer_id=transfer_id, type=type_, payload=payload)
        self.db.add(evt)