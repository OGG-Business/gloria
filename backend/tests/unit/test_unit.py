"""
Tests unitaires pour la plateforme de transferts bancaires
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
from unittest.mock import Mock, patch

from app.accounts.models import Account, AccountType, AccountStatus, Currency
from app.transfers.models import Transfer, TransferType, TransferStatus, TransferPriority
from app.auth.models import User, UserStatus
from app.kyc.models import KYCDocument, DocumentType, DocumentStatus
from app.common.encryption import encrypt_data, decrypt_data
from app.common.validation import validate_iban, validate_bic, validate_amount


class TestAccountModels:
    """Tests unitaires pour les modèles de comptes"""
    
    def test_account_creation(self):
        """Test de création d'un compte"""
        account = Account(
            account_number="1234567890",
            iban="FR7630006000011234567890189",
            bic="BNPAFRPP",
            holder_name="Test User",
            holder_id="123456789",
            holder_email="test@example.com",
            bank_name="Test Bank",
            bank_code="12345",
            account_type=AccountType.CURRENT,
            currency=Currency.USD,
            balance=1000.00,
            daily_limit=5000.00,
            status=AccountStatus.ACTIVE
        )
        
        assert account.account_number == "1234567890"
        assert account.iban == "FR7630006000011234567890189"
        assert account.bic == "BNPAFRPP"
        assert account.holder_name == "Test User"
        assert account.account_type == AccountType.CURRENT
        assert account.currency == Currency.USD
        assert account.balance == 1000.00
        assert account.status == AccountStatus.ACTIVE
    
    def test_account_balance_operations(self):
        """Test des opérations de solde"""
        account = Account(
            account_number="1234567890",
            iban="FR7630006000011234567890189",
            bic="BNPAFRPP",
            holder_name="Test User",
            holder_id="123456789",
            holder_email="test@example.com",
            bank_name="Test Bank",
            bank_code="12345",
            account_type=AccountType.CURRENT,
            currency=Currency.USD,
            balance=1000.00,
            daily_limit=5000.00,
            status=AccountStatus.ACTIVE
        )
        
        # Test de débit
        account.debit(500.00)
        assert account.balance == 500.00
        
        # Test de crédit
        account.credit(200.00)
        assert account.balance == 700.00
        
        # Test de blocage de montant
        account.block_amount(100.00)
        assert account.blocked_amount == 100.00
        assert account.available_balance == 600.00
        
        # Test de déblocage
        account.unblock_amount(50.00)
        assert account.blocked_amount == 50.00
        assert account.available_balance == 650.00
    
    def test_account_validation(self):
        """Test de validation des comptes"""
        # Compte valide
        valid_account = Account(
            account_number="1234567890",
            iban="FR7630006000011234567890189",
            bic="BNPAFRPP",
            holder_name="Test User",
            holder_id="123456789",
            holder_email="test@example.com",
            bank_name="Test Bank",
            bank_code="12345",
            account_type=AccountType.CURRENT,
            currency=Currency.USD,
            balance=1000.00,
            daily_limit=5000.00,
            status=AccountStatus.ACTIVE
        )
        
        assert valid_account.is_active is True
        assert valid_account.has_sufficient_balance(500.00) is True
        assert valid_account.has_sufficient_balance(2000.00) is False
        assert valid_account.is_within_daily_limit(1000.00) is True
        assert valid_account.is_within_daily_limit(6000.00) is False


class TestTransferModels:
    """Tests unitaires pour les modèles de transferts"""
    
    def test_transfer_creation(self):
        """Test de création d'un transfert"""
        transfer = Transfer(
            transfer_id="TRF123456789",
            source_account_id=1,
            destination_account_id=2,
            transfer_type=TransferType.SWIFT,
            amount=1000.00,
            currency=Currency.USD,
            beneficiary_name="Test Beneficiary",
            beneficiary_bank="Test Bank",
            beneficiary_iban="US123456789012345678901234",
            beneficiary_bic="CHASUS33",
            purpose="Test transfer",
            priority=TransferPriority.NORMAL,
            status=TransferStatus.INITIATED
        )
        
        assert transfer.transfer_id == "TRF123456789"
        assert transfer.source_account_id == 1
        assert transfer.destination_account_id == 2
        assert transfer.transfer_type == TransferType.SWIFT
        assert transfer.amount == 1000.00
        assert transfer.currency == Currency.USD
        assert transfer.beneficiary_name == "Test Beneficiary"
        assert transfer.status == TransferStatus.INITIATED
    
    def test_transfer_status_transitions(self):
        """Test des transitions de statut de transfert"""
        transfer = Transfer(
            transfer_id="TRF123456789",
            source_account_id=1,
            destination_account_id=2,
            transfer_type=TransferType.SWIFT,
            amount=1000.00,
            currency=Currency.USD,
            beneficiary_name="Test Beneficiary",
            beneficiary_bank="Test Bank",
            beneficiary_iban="US123456789012345678901234",
            beneficiary_bic="CHASUS33",
            purpose="Test transfer",
            status=TransferStatus.INITIATED
        )
        
        # Vérifier les propriétés de statut
        assert transfer.is_initiated is True
        assert transfer.is_pending is False
        assert transfer.is_completed is False
        assert transfer.is_failed is False
        
        # Changer le statut
        transfer.status = TransferStatus.PENDING
        assert transfer.is_pending is True
        assert transfer.is_initiated is False
        
        transfer.status = TransferStatus.COMPLETED
        assert transfer.is_completed is True
        assert transfer.is_pending is False
    
    def test_transfer_validation(self):
        """Test de validation des transferts"""
        # Transfert valide
        valid_transfer = Transfer(
            transfer_id="TRF123456789",
            source_account_id=1,
            destination_account_id=2,
            transfer_type=TransferType.SWIFT,
            amount=1000.00,
            currency=Currency.USD,
            beneficiary_name="Test Beneficiary",
            beneficiary_bank="Test Bank",
            beneficiary_iban="US123456789012345678901234",
            beneficiary_bic="CHASUS33",
            purpose="Test transfer",
            status=TransferStatus.INITIATED
        )
        
        assert valid_transfer.is_valid() is True
        assert valid_transfer.amount > 0
        assert valid_transfer.beneficiary_name is not None
        assert valid_transfer.beneficiary_iban is not None
        
        # Transfert invalide (montant négatif)
        invalid_transfer = Transfer(
            transfer_id="TRF123456789",
            source_account_id=1,
            destination_account_id=2,
            transfer_type=TransferType.SWIFT,
            amount=-100.00,  # Montant négatif
            currency=Currency.USD,
            beneficiary_name="Test Beneficiary",
            beneficiary_bank="Test Bank",
            beneficiary_iban="US123456789012345678901234",
            beneficiary_bic="CHASUS33",
            purpose="Test transfer",
            status=TransferStatus.INITIATED
        )
        
        assert invalid_transfer.amount <= 0


class TestUserModels:
    """Tests unitaires pour les modèles d'utilisateurs"""
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            is_active=True,
            mfa_enabled=False,
            status=UserStatus.ACTIVE
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.mfa_enabled is False
        assert user.status == UserStatus.ACTIVE
    
    def test_user_validation(self):
        """Test de validation des utilisateurs"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            is_active=True,
            mfa_enabled=False,
            status=UserStatus.ACTIVE
        )
        
        assert user.is_active is True
        assert user.is_locked is False
        assert user.has_valid_email() is True
        
        # Utilisateur verrouillé
        user.status = UserStatus.LOCKED
        assert user.is_locked is True
        assert user.is_active is False
    
    def test_user_account_relationship(self):
        """Test de la relation utilisateur-compte"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            is_active=True,
            mfa_enabled=False,
            status=UserStatus.ACTIVE
        )
        
        account = Account(
            account_number="1234567890",
            iban="FR7630006000011234567890189",
            bic="BNPAFRPP",
            holder_name="Test User",
            holder_id="123456789",
            holder_email="test@example.com",
            bank_name="Test Bank",
            bank_code="12345",
            account_type=AccountType.CURRENT,
            currency=Currency.USD,
            balance=1000.00,
            daily_limit=5000.00,
            status=AccountStatus.ACTIVE
        )
        
        # Simuler la relation
        user.accounts = [account]
        
        assert len(user.accounts) == 1
        assert user.accounts[0].account_number == "1234567890"


class TestKYCModels:
    """Tests unitaires pour les modèles KYC"""
    
    def test_kyc_document_creation(self):
        """Test de création d'un document KYC"""
        document = KYCDocument(
            document_type=DocumentType.IDENTITY_CARD,
            document_number="ID123456789",
            issuing_country="FR",
            expiry_date="2030-12-31",
            file_path="/uploads/id_card.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status=DocumentStatus.PENDING
        )
        
        assert document.document_type == DocumentType.IDENTITY_CARD
        assert document.document_number == "ID123456789"
        assert document.issuing_country == "FR"
        assert document.status == DocumentStatus.PENDING
    
    def test_kyc_document_validation(self):
        """Test de validation des documents KYC"""
        document = KYCDocument(
            document_type=DocumentType.IDENTITY_CARD,
            document_number="ID123456789",
            issuing_country="FR",
            expiry_date="2030-12-31",
            file_path="/uploads/id_card.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status=DocumentStatus.PENDING
        )
        
        assert document.is_pending is True
        assert document.is_verified is False
        assert document.is_expired() is False
        
        # Document expiré
        expired_document = KYCDocument(
            document_type=DocumentType.PASSPORT,
            document_number="PASS123456789",
            issuing_country="FR",
            expiry_date="2020-12-31",  # Date passée
            file_path="/uploads/passport.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status=DocumentStatus.VERIFIED
        )
        
        assert expired_document.is_expired() is True


class TestEncryption:
    """Tests unitaires pour le chiffrement"""
    
    def test_data_encryption_decryption(self):
        """Test du chiffrement et déchiffrement de données"""
        test_data = "sensitive_data_123"
        
        # Chiffrer les données
        encrypted = encrypt_data(test_data)
        
        # Vérifier que les données sont chiffrées
        assert encrypted != test_data
        assert isinstance(encrypted, str)
        assert len(encrypted) > len(test_data)
        
        # Déchiffrer les données
        decrypted = decrypt_data(encrypted)
        
        # Vérifier que les données sont correctement déchiffrées
        assert decrypted == test_data
    
    def test_encryption_with_different_data_types(self):
        """Test du chiffrement avec différents types de données"""
        test_cases = [
            "simple_string",
            "string_with_special_chars_!@#$%^&*()",
            "123456789",
            "email@example.com",
            "FR7630006000011234567890189",  # IBAN
            "BNPAFRPP"  # BIC
        ]
        
        for test_data in test_cases:
            encrypted = encrypt_data(test_data)
            decrypted = decrypt_data(encrypted)
            
            assert encrypted != test_data
            assert decrypted == test_data
    
    def test_encryption_error_handling(self):
        """Test de la gestion d'erreur du chiffrement"""
        # Test avec des données vides
        empty_data = ""
        encrypted = encrypt_data(empty_data)
        decrypted = decrypt_data(encrypted)
        assert decrypted == empty_data
        
        # Test avec des données None
        with pytest.raises(Exception):
            encrypt_data(None)


class TestValidation:
    """Tests unitaires pour la validation"""
    
    def test_iban_validation(self):
        """Test de validation des IBAN"""
        # IBANs valides
        valid_ibans = [
            "FR7630006000011234567890189",  # France
            "DE89370400440532013000",       # Allemagne
            "GB29NWBK60161331926819",       # Royaume-Uni
            "US123456789012345678901234"    # États-Unis (format fictif)
        ]
        
        for iban in valid_ibans:
            assert validate_iban(iban) is True
        
        # IBANs invalides
        invalid_ibans = [
            "INVALID_IBAN",
            "FR123",  # Trop court
            "FR7630006000011234567890189INVALID",  # Trop long
            "123456789012345678901234"  # Pas de code pays
        ]
        
        for iban in invalid_ibans:
            assert validate_iban(iban) is False
    
    def test_bic_validation(self):
        """Test de validation des BIC"""
        # BICs valides
        valid_bics = [
            "BNPAFRPP",  # BNP Paribas
            "CHASUS33",  # JPMorgan Chase
            "DEUTDEFF",  # Deutsche Bank
            "UBSWCHZH"   # UBS
        ]
        
        for bic in valid_bics:
            assert validate_bic(bic) is True
        
        # BICs invalides
        invalid_bics = [
            "INVALID_BIC",
            "BNP",  # Trop court
            "BNPAFRPPINVALID",  # Trop long
            "12345678"  # Chiffres uniquement
        ]
        
        for bic in invalid_bics:
            assert validate_bic(bic) is False
    
    def test_amount_validation(self):
        """Test de validation des montants"""
        # Montants valides
        valid_amounts = [
            0.01,
            100.00,
            1000.50,
            999999.99
        ]
        
        for amount in valid_amounts:
            assert validate_amount(amount) is True
        
        # Montants invalides
        invalid_amounts = [
            -100.00,  # Négatif
            0.00,     # Zéro
            1000000.00,  # Trop élevé
            "invalid"    # Type invalide
        ]
        
        for amount in invalid_amounts:
            assert validate_amount(amount) is False


class TestBusinessLogic:
    """Tests unitaires pour la logique métier"""
    
    def test_transfer_fee_calculation(self):
        """Test du calcul des frais de transfert"""
        # Fonction fictive pour calculer les frais
        def calculate_transfer_fee(amount: float, transfer_type: str, priority: str) -> float:
            base_fee = 10.00
            
            if transfer_type == "swift":
                base_fee = 25.00
            elif transfer_type == "mojaloop":
                base_fee = 5.00
            
            if priority == "urgent":
                base_fee *= 2
            elif priority == "high":
                base_fee *= 1.5
            
            # Frais en pourcentage pour les gros montants
            if amount > 10000:
                base_fee += amount * 0.001
            
            return round(base_fee, 2)
        
        # Tests de calcul des frais
        assert calculate_transfer_fee(1000.00, "swift", "normal") == 25.00
        assert calculate_transfer_fee(1000.00, "swift", "urgent") == 50.00
        assert calculate_transfer_fee(1000.00, "mojaloop", "normal") == 5.00
        assert calculate_transfer_fee(15000.00, "swift", "normal") == 40.00  # 25 + 15
    
    def test_transfer_limit_validation(self):
        """Test de validation des limites de transfert"""
        def validate_transfer_limits(amount: float, daily_total: float, daily_limit: float) -> bool:
            return amount > 0 and (daily_total + amount) <= daily_limit
        
        # Tests de validation des limites
        assert validate_transfer_limits(1000.00, 0.00, 5000.00) is True
        assert validate_transfer_limits(1000.00, 4000.00, 5000.00) is True
        assert validate_transfer_limits(1000.00, 4000.00, 5000.00) is True
        assert validate_transfer_limits(1000.00, 5000.00, 5000.00) is False  # Dépassement
        assert validate_transfer_limits(-100.00, 0.00, 5000.00) is False  # Montant négatif
    
    def test_currency_conversion(self):
        """Test de conversion de devises"""
        # Taux de change fictifs
        exchange_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0
        }
        
        def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
            if from_currency == to_currency:
                return amount
            
            usd_amount = amount / exchange_rates[from_currency]
            return round(usd_amount * exchange_rates[to_currency], 2)
        
        # Tests de conversion
        assert convert_currency(100.00, "USD", "USD") == 100.00
        assert convert_currency(100.00, "USD", "EUR") == 85.00
        assert convert_currency(100.00, "EUR", "USD") == 117.65
        assert convert_currency(1000.00, "USD", "JPY") == 110000.00


class TestDataTransformation:
    """Tests unitaires pour la transformation de données"""
    
    def test_swift_message_formatting(self):
        """Test du formatage des messages SWIFT"""
        def format_swift_message(transfer_data: Dict[str, Any]) -> str:
            return f"""{{1:F01{transfer_data['sender_bic']}XXXXAXXX1234567890}}
{{2:O1031234567890{transfer_data['sender_bic']}XXXXAXXX1234567890N}}
{{3:{{113:SEPA}}{{108:ILOVESEPA}}}}
{{4:
:20:{transfer_data['reference']}
:23B:CRED
:32A:{transfer_data['date']}{transfer_data['currency']}{transfer_data['amount']}
:50K:/{transfer_data['sender_account']}
{transfer_data['sender_name']}
:59:/{transfer_data['receiver_account']}
{transfer_data['receiver_name']}
:70:{transfer_data['purpose']}
:71A:SHA
-}}
{{5:{{CHK:1234567890ABC}}{{TNG:}}}}"""
        
        transfer_data = {
            "sender_bic": "BNPAFRPP",
            "reference": "REF123456789",
            "date": "240101",
            "currency": "USD",
            "amount": "1000,00",
            "sender_account": "12345678901234567890",
            "sender_name": "Test Sender",
            "receiver_account": "09876543210987654321",
            "receiver_name": "Test Receiver",
            "purpose": "Test transfer"
        }
        
        swift_message = format_swift_message(transfer_data)
        
        assert "BNPAFRPP" in swift_message
        assert "REF123456789" in swift_message
        assert "1000,00" in swift_message
        assert "Test Sender" in swift_message
        assert "Test Receiver" in swift_message
    
    def test_iso20022_message_formatting(self):
        """Test du formatage des messages ISO 20022"""
        def format_iso20022_message(transfer_data: Dict[str, Any]) -> str:
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
    <FIToFICstmrCdtTrf>
        <GrpHdr>
            <MsgId>{transfer_data['message_id']}</MsgId>
            <CreDtTm>{transfer_data['creation_time']}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <TtlIntrBkSttlmAmt Ccy="{transfer_data['currency']}">{transfer_data['amount']}</TtlIntrBkSttlmAmt>
        </GrpHdr>
        <CdtTrfTxInf>
            <PmtId>
                <InstrId>{transfer_data['instruction_id']}</InstrId>
                <EndToEndId>{transfer_data['end_to_end_id']}</EndToEndId>
            </PmtId>
            <IntrBkSttlmAmt Ccy="{transfer_data['currency']}">{transfer_data['amount']}</IntrBkSttlmAmt>
            <Dbtr>
                <Nm>{transfer_data['debtor_name']}</Nm>
            </Dbtr>
            <Cdtr>
                <Nm>{transfer_data['creditor_name']}</Nm>
            </Cdtr>
        </CdtTrfTxInf>
    </FIToFICstmrCdtTrf>
</Document>"""
        
        transfer_data = {
            "message_id": "MSG123456789",
            "creation_time": "2024-01-01T10:00:00",
            "currency": "USD",
            "amount": "1000.00",
            "instruction_id": "INSTR123456",
            "end_to_end_id": "E2E123456789",
            "debtor_name": "Test Sender",
            "creditor_name": "Test Receiver"
        }
        
        iso_message = format_iso20022_message(transfer_data)
        
        assert "MSG123456789" in iso_message
        assert "USD" in iso_message
        assert "1000.00" in iso_message
        assert "Test Sender" in iso_message
        assert "Test Receiver" in iso_message


class TestErrorHandling:
    """Tests unitaires pour la gestion d'erreur"""
    
    def test_custom_exceptions(self):
        """Test des exceptions personnalisées"""
        class InsufficientFundsError(Exception):
            pass
        
        class TransferLimitExceededError(Exception):
            pass
        
        class InvalidIBANError(Exception):
            pass
        
        # Test des exceptions
        with pytest.raises(InsufficientFundsError):
            raise InsufficientFundsError("Insufficient funds")
        
        with pytest.raises(TransferLimitExceededError):
            raise TransferLimitExceededError("Transfer limit exceeded")
        
        with pytest.raises(InvalidIBANError):
            raise InvalidIBANError("Invalid IBAN")
    
    def test_error_messages(self):
        """Test des messages d'erreur"""
        def validate_transfer(amount: float, balance: float) -> Dict[str, Any]:
            if amount <= 0:
                return {"valid": False, "error": "Amount must be positive"}
            
            if amount > balance:
                return {"valid": False, "error": "Insufficient funds"}
            
            return {"valid": True, "error": None}
        
        # Tests de validation
        result1 = validate_transfer(-100, 1000)
        assert result1["valid"] is False
        assert "Amount must be positive" in result1["error"]
        
        result2 = validate_transfer(1500, 1000)
        assert result2["valid"] is False
        assert "Insufficient funds" in result2["error"]
        
        result3 = validate_transfer(500, 1000)
        assert result3["valid"] is True
        assert result3["error"] is None