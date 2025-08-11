from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from typing import Optional, List, Dict
from .models import Account, Transfer, TransferEvent, AuditLog

class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, owner_name: str, iban: str, bic: str, external_id: Optional[str] = None) -> Account:
        stmt = insert(Account).values(owner_name=owner_name, iban=iban, bic=bic, external_id=external_id).returning(Account)
        res = await self.session.execute(stmt)
        (acc,) = res.fetchone()
        await self.session.commit()
        return acc

class TransferRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict) -> Transfer:
        stmt = insert(Transfer).values(**data).returning(Transfer)
        res = await self.session.execute(stmt)
        (t,) = res.fetchone()
        await self.session.commit()
        return t

class TransferEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, transfer_id: int, event_type: str, payload: Dict) -> TransferEvent:
        stmt = insert(TransferEvent).values(transfer_id=transfer_id, event_type=event_type, payload=payload).returning(TransferEvent)
        res = await self.session.execute(stmt)
        (ev,) = res.fetchone()
        await self.session.commit()
        return ev

class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, action: str, subject: str, actor: str, details: Dict, prev_hash: Optional[str], hash_value: str) -> AuditLog:
        stmt = insert(AuditLog).values(action=action, subject=subject, actor=actor, details=details, prev_hash=prev_hash, hash=hash_value).returning(AuditLog)
        res = await self.session.execute(stmt)
        (log,) = res.fetchone()
        await self.session.commit()
        return log