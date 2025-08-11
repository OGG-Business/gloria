import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.transfers.service import TransferOrchestrator
from app.models import Account

@pytest.mark.asyncio
async def test_orchestrator_dry_run(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(__import__('app.db').db.Base.metadata.create_all)
    async with AsyncSession() as session:
        acct = Account(user_id=0, iban="DE12500105170648489890", bic="DEUTDEFF", display_name="Test", sensitive_metadata=b"x")
        session.add(acct)
        await session.commit()
        await session.refresh(acct)
        orch = TransferOrchestrator(session)
        tr = await orch.create_transfer(acct.id, "FR1420041010050500013M02606", "DEUTDEFF", 10.0, "USD", "REF", True)
        assert tr.status.name in ("PENDING","INITIATED")