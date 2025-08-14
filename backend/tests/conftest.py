"""
Configuration pytest avec fixtures communes pour les tests
"""
import pytest
import asyncio
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.common.database import Base, get_db
from app.config import get_settings
from app.accounts.models import Account, AccountType, AccountStatus, Currency
from app.auth.models import User, UserStatus
from app.transfers.models import Transfer, TransferType, TransferStatus
from app.kyc.models import KYCDocument, DocumentType, DocumentStatus


# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la fonction get_db pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Créer une boucle d'événements pour les tests asynchrones"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_engine():
    """Créer le moteur de base de données de test"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Créer une session de base de données pour les tests"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Créer un client de test FastAPI"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Données de test pour un utilisateur"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "is_active": True,
        "mfa_enabled": False
    }


@pytest.fixture
def test_user(db_session, test_user_data) -> User:
    """Créer un utilisateur de test"""
    from app.auth.services import get_password_hash
    
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        phone=test_user_data["phone"],
        is_active=test_user_data["is_active"],
        mfa_enabled=test_user_data["mfa_enabled"],
        status=UserStatus.ACTIVE
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_account_data() -> Dict[str, Any]:
    """Données de test pour un compte"""
    return {
        "account_number": "1234567890",
        "iban": "FR7630006000011234567890189",
        "bic": "BNPAFRPP",
        "holder_name": "Test User",
        "holder_id": "123456789",
        "holder_email": "test@example.com",
        "bank_name": "Test Bank",
        "bank_code": "12345",
        "account_type": AccountType.CURRENT,
        "currency": Currency.USD,
        "balance": 10000.00,
        "daily_limit": 5000.00,
        "status": AccountStatus.ACTIVE
    }


@pytest.fixture
def test_account(db_session, test_user, test_account_data) -> Account:
    """Créer un compte de test"""
    account = Account(
        user_id=test_user.id,
        account_number=test_account_data["account_number"],
        iban=test_account_data["iban"],
        bic=test_account_data["bic"],
        holder_name=test_account_data["holder_name"],
        holder_id=test_account_data["holder_id"],
        holder_email=test_account_data["holder_email"],
        bank_name=test_account_data["bank_name"],
        bank_code=test_account_data["bank_code"],
        account_type=test_account_data["account_type"],
        currency=test_account_data["currency"],
        balance=test_account_data["balance"],
        daily_limit=test_account_data["daily_limit"],
        status=test_account_data["status"]
    )
    
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    
    return account


@pytest.fixture
def test_transfer_data() -> Dict[str, Any]:
    """Données de test pour un transfert"""
    return {
        "transfer_type": TransferType.SWIFT,
        "amount": 1000.00,
        "currency": Currency.USD,
        "beneficiary_name": "Test Beneficiary",
        "beneficiary_bank": "Test Bank",
        "beneficiary_iban": "US123456789012345678901234",
        "beneficiary_bic": "CHASUS33",
        "purpose": "Test transfer",
        "priority": "normal"
    }


@pytest.fixture
def test_transfer(db_session, test_account, test_transfer_data) -> Transfer:
    """Créer un transfert de test"""
    transfer = Transfer(
        source_account_id=test_account.id,
        destination_account_id=test_account.id,  # Même compte pour le test
        transfer_type=test_transfer_data["transfer_type"],
        amount=test_transfer_data["amount"],
        currency=test_transfer_data["currency"],
        beneficiary_name=test_transfer_data["beneficiary_name"],
        beneficiary_bank=test_transfer_data["beneficiary_bank"],
        beneficiary_iban=test_transfer_data["beneficiary_iban"],
        beneficiary_bic=test_transfer_data["beneficiary_bic"],
        purpose=test_transfer_data["purpose"],
        status=TransferStatus.INITIATED
    )
    
    db_session.add(transfer)
    db_session.commit()
    db_session.refresh(transfer)
    
    return transfer


@pytest.fixture
def test_kyc_document_data() -> Dict[str, Any]:
    """Données de test pour un document KYC"""
    return {
        "document_type": DocumentType.IDENTITY_CARD,
        "document_number": "ID123456789",
        "issuing_country": "FR",
        "expiry_date": "2030-12-31",
        "file_path": "/test/path/document.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf",
        "status": DocumentStatus.PENDING
    }


@pytest.fixture
def test_kyc_document(db_session, test_user, test_kyc_document_data) -> KYCDocument:
    """Créer un document KYC de test"""
    document = KYCDocument(
        user_id=test_user.id,
        document_type=test_kyc_document_data["document_type"],
        document_number=test_kyc_document_data["document_number"],
        issuing_country=test_kyc_document_data["issuing_country"],
        expiry_date=test_kyc_document_data["expiry_date"],
        file_path=test_kyc_document_data["file_path"],
        file_size=test_kyc_document_data["file_size"],
        mime_type=test_kyc_document_data["mime_type"],
        status=test_kyc_document_data["status"]
    )
    
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    return document


@pytest.fixture
def test_utils():
    """Utilitaires pour créer des objets de test"""
    class TestUtils:
        @staticmethod
        def create_test_user(db_session: Session, user_data: Dict[str, Any]) -> User:
            """Créer un utilisateur de test"""
            from app.auth.services import get_password_hash
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                first_name=user_data.get("first_name", "Test"),
                last_name=user_data.get("last_name", "User"),
                phone=user_data.get("phone", "+1234567890"),
                is_active=user_data.get("is_active", True),
                mfa_enabled=user_data.get("mfa_enabled", False),
                status=UserStatus.ACTIVE
            )
            
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
            return user
        
        @staticmethod
        def create_test_account(db_session: Session, account_data: Dict[str, Any], user_id: int) -> Account:
            """Créer un compte de test"""
            account = Account(
                user_id=user_id,
                account_number=account_data["account_number"],
                iban=account_data["iban"],
                bic=account_data["bic"],
                holder_name=account_data["holder_name"],
                holder_id=account_data["holder_id"],
                holder_email=account_data["holder_email"],
                bank_name=account_data["bank_name"],
                bank_code=account_data["bank_code"],
                account_type=account_data["account_type"],
                currency=account_data["currency"],
                balance=account_data.get("balance", 0.00),
                daily_limit=account_data.get("daily_limit", 1000.00),
                status=account_data.get("status", AccountStatus.ACTIVE)
            )
            
            db_session.add(account)
            db_session.commit()
            db_session.refresh(account)
            
            return account
        
        @staticmethod
        def create_test_transfer(db_session: Session, transfer_data: Dict[str, Any]) -> Transfer:
            """Créer un transfert de test"""
            transfer = Transfer(
                source_account_id=transfer_data["source_account_id"],
                destination_account_id=transfer_data["destination_account_id"],
                transfer_type=transfer_data["transfer_type"],
                amount=transfer_data["amount"],
                currency=transfer_data["currency"],
                beneficiary_name=transfer_data["beneficiary_name"],
                beneficiary_bank=transfer_data["beneficiary_bank"],
                beneficiary_iban=transfer_data["beneficiary_iban"],
                beneficiary_bic=transfer_data["beneficiary_bic"],
                purpose=transfer_data.get("purpose", "Test transfer"),
                status=TransferStatus.INITIATED
            )
            
            db_session.add(transfer)
            db_session.commit()
            db_session.refresh(transfer)
            
            return transfer
    
    return TestUtils()


@pytest.fixture
def mock_settings():
    """Mock des paramètres de configuration"""
    return {
        "database": {
            "url": "sqlite:///./test.db",
            "echo": False
        },
        "security": {
            "secret_key": "test-secret-key",
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "encryption_key": "test-encryption-key"
        },
        "swift": {
            "bic": "TESTBIC",
            "cert_path": "/test/cert.pem",
            "key_path": "/test/key.pem",
            "endpoint": "https://test.swift.com",
            "timeout": 30,
            "dry_run": True
        },
        "mojaloop": {
            "endpoint": "https://test.mojaloop.com",
            "timeout": 30,
            "dry_run": True
        },
        "redis": {
            "url": "redis://localhost:6379/0"
        },
        "notifications": {
            "smtp_host": "localhost",
            "smtp_port": 587,
            "smtp_username": "test",
            "smtp_password": "test",
            "twilio_account_sid": "test",
            "twilio_auth_token": "test",
            "twilio_phone_number": "+1234567890"
        },
        "monitoring": {
            "prometheus_enabled": True,
            "logging_level": "INFO",
            "tracing_enabled": False
        },
        "kyc": {
            "transfer_limit_usd": 10000,
            "sanctions_api_url": "https://test.sanctions.com",
            "sanctions_api_key": "test-key",
            "document_storage_path": "/test/documents"
        }
    }


@pytest.fixture
def mock_vault():
    """Mock de HashiCorp Vault"""
    class MockVault:
        def __init__(self):
            self.secrets = {
                "swift/cert": "test-cert-content",
                "swift/key": "test-key-content",
                "swift/password": "test-password",
                "database/password": "test-db-password",
                "encryption/key": "test-encryption-key"
            }
        
        def read_secret(self, path: str) -> Dict[str, Any]:
            """Lire un secret depuis Vault"""
            if path in self.secrets:
                return {"data": {"value": self.secrets[path]}}
            return {"data": {"value": None}}
        
        def write_secret(self, path: str, data: Dict[str, Any]) -> None:
            """Écrire un secret dans Vault"""
            self.secrets[path] = data.get("value", "")
    
    return MockVault()


@pytest.fixture
def mock_swift_connector():
    """Mock du connecteur SWIFT"""
    class MockSwiftConnector:
        def __init__(self, config: Dict[str, Any]):
            self.config = config
            self.messages_sent = []
        
        def create_mt103_message(self, transfer) -> str:
            """Créer un message SWIFT MT103"""
            return f"MT103 message for transfer {transfer.id}"
        
        def create_mt910_message(self, account, amount, currency, reference) -> str:
            """Créer un message SWIFT MT910"""
            return f"MT910 message for account {account.id}"
        
        def validate_swift_message(self, message: str) -> bool:
            """Valider un message SWIFT"""
            return "MT103" in message or "MT910" in message
        
        async def send_message(self, transfer) -> Dict[str, Any]:
            """Envoyer un message SWIFT"""
            message = self.create_mt103_message(transfer)
            self.messages_sent.append(message)
            return {
                "success": True,
                "message_id": f"SWIFT{transfer.id}",
                "swift_message": message,
                "dry_run": self.config.get("dry_run", True)
            }
        
        def test_connectivity(self) -> Dict[str, Any]:
            """Tester la connectivité SWIFT"""
            return {
                "success": True,
                "endpoint": self.config.get("endpoint", "https://test.swift.com")
            }
    
    return MockSwiftConnector


@pytest.fixture
def mock_mojaloop_connector():
    """Mock du connecteur Mojaloop"""
    class MockMojaloopConnector:
        def __init__(self, config: Dict[str, Any]):
            self.config = config
            self.transfers_sent = []
        
        async def send_transfer(self, transfer) -> Dict[str, Any]:
            """Envoyer un transfert Mojaloop"""
            self.transfers_sent.append(transfer)
            return {
                "success": True,
                "transfer_id": f"MOJALOOP{transfer.id}",
                "status": "ACCEPTED",
                "dry_run": self.config.get("dry_run", True)
            }
        
        def test_connectivity(self) -> Dict[str, Any]:
            """Tester la connectivité Mojaloop"""
            return {
                "success": True,
                "endpoint": self.config.get("endpoint", "https://test.mojaloop.com")
            }
    
    return MockMojaloopConnector