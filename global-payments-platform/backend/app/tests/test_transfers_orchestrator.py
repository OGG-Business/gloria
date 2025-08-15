import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.transfers.service import TransferOrchestrator
from app.models import Account, TransferStatus

# Mock Settings object for the connector
@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.connector_azqore_api_url = "https://fake-api.azqore.com"
    settings.connector_azqore_bic = "SBXACHSS"
    # This test version uses a static token, ignoring the Keycloak service logic
    settings.connector_azqore_jwt_token = "fake-jwt-token"
    return settings

# Mock AzqoreConnector to simplify testing the orchestrator
@pytest.fixture
def mock_azqore_connector(monkeypatch, mock_settings):
    mock = MagicMock()
    mock.get_quotation = AsyncMock(return_value={"id": "quote_123"})
    mock.create_transaction = AsyncMock(return_value={"id": "txn_456"})
    mock.confirm_transaction = AsyncMock(return_value={"status": "CONFIRMED"})

    # Replace the real connector with our mock
    monkeypatch.setattr(
        "app.transfers.service.AzqoreConnector",
        lambda settings: mock
    )
    # Ensure the orchestrator gets the mocked settings
    monkeypatch.setattr("app.transfers.service.settings", mock_settings)
    return mock

@pytest.mark.asyncio
async def test_orchestrator_azqore_workflow(mock_azqore_connector):
    # Setup in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession() as session:
        # 1. Arrange
        acct = Account(user_id=1, iban="DE12500105170648489890", bic="DEUTDEFF", display_name="Test Account")
        session.add(acct)
        await session.commit()
        await session.refresh(acct)

        # 2. Act
        orch = TransferOrchestrator(session)
        transfer = await orch.create_transfer(
            debtor_account_id=acct.id,
            creditor_iban="FR1420041010050500013M02606",
            creditor_bic="AGRIFRPP",
            amount=100.0,
            currency="EUR",
            reference="Test Payment",
            dry_run=False
        )

        # 3. Assert
        mock_azqore_connector.get_quotation.assert_called_once()
        mock_azqore_connector.create_transaction.assert_called_once()
        mock_azqore_connector.confirm_transaction.assert_called_once()

        assert transfer.status == TransferStatus.PENDING
        assert transfer.quotation_id == "quote_123"
        assert transfer.transaction_id == "txn_456"