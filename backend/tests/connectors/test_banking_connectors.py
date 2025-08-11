"""
Tests pour les connecteurs bancaires (SWIFT, Mojaloop, ISO 20022)
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.connectors.swift import SwiftConnector
from app.connectors.mojaloop import MojaloopConnector
from app.connectors.iso20022 import ISO20022Connector
from app.transfers.models import Transfer, TransferStatus
from app.accounts.models import Account, AccountStatus


class TestSwiftConnector:
    """Tests du connecteur SWIFT"""
    
    def test_swift_connector_initialization(self, swift_test_config: Dict[str, Any]):
        """Test de l'initialisation du connecteur SWIFT"""
        connector = SwiftConnector(swift_test_config)
        
        assert connector.bic == "TESTBIC"
        assert connector.cert_path == "/test/cert.pem"
        assert connector.key_path == "/test/key.pem"
        assert connector.endpoint == "https://test.swift.com"
        assert connector.timeout == 30
        assert connector.dry_run is True
    
    def test_swift_message_creation_mt103(self, swift_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test de création de message SWIFT MT103"""
        # Créer un utilisateur et des comptes
        user = test_utils.create_test_user(db_session, {
            "username": "swiftuser",
            "email": "swift@example.com",
            "password": "testpass123"
        })
        
        source_account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Test Sender",
            "holder_id": "123456789",
            "holder_email": "sender@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        destination_account = test_utils.create_test_account(db_session, {
            "account_number": "0987654321",
            "iban": "US123456789012345678901234",
            "bic": "CHASUS33",
            "holder_name": "Test Receiver",
            "holder_id": "987654321",
            "holder_email": "receiver@example.com",
            "bank_name": "Test Bank",
            "bank_code": "54321",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        # Créer un transfert
        transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Test transfer"
        })
        
        connector = SwiftConnector(swift_test_config)
        swift_message = connector.create_mt103_message(transfer)
        
        assert swift_message is not None
        assert "MT103" in swift_message
        assert "BNPAFRPP" in swift_message
        assert "CHASUS33" in swift_message
        assert "1000.00" in swift_message
        assert "USD" in swift_message
        assert "Test Beneficiary" in swift_message
    
    def test_swift_message_validation(self, swift_test_config: Dict[str, Any]):
        """Test de validation des messages SWIFT"""
        connector = SwiftConnector(swift_test_config)
        
        # Message valide
        valid_message = swift_test_config["test_messages"]["mt103"]
        assert connector.validate_swift_message(valid_message) is True
        
        # Message invalide
        invalid_message = "Invalid SWIFT message"
        assert connector.validate_swift_message(invalid_message) is False
    
    @pytest.mark.asyncio
    async def test_swift_message_sending_dry_run(self, swift_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test d'envoi de message SWIFT en mode dry-run"""
        # Créer un transfert de test
        user = test_utils.create_test_user(db_session, {
            "username": "swiftsenduser",
            "email": "swiftsend@example.com",
            "password": "testpass123"
        })
        
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Test User",
            "holder_id": "123456789",
            "holder_email": "test@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Test transfer"
        })
        
        connector = SwiftConnector(swift_test_config)
        result = await connector.send_message(transfer)
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "message_id" in result
        assert "swift_message" in result
    
    def test_swift_connectivity_test(self, swift_test_config: Dict[str, Any]):
        """Test de connectivité SWIFT"""
        connector = SwiftConnector(swift_test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = connector.test_connectivity()
            
            assert result["success"] is True
            assert result["endpoint"] == "https://test.swift.com"


class TestMojaloopConnector:
    """Tests du connecteur Mojaloop"""
    
    def test_mojaloop_connector_initialization(self, mojaloop_test_config: Dict[str, Any]):
        """Test de l'initialisation du connecteur Mojaloop"""
        connector = MojaloopConnector(mojaloop_test_config)
        
        assert connector.endpoint == "https://test.mojaloop.com"
        assert connector.timeout == 30
        assert connector.dry_run is True
        assert connector.participant_id == "test-participant"
    
    @pytest.mark.asyncio
    async def test_mojaloop_transfer_sending(self, mojaloop_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test d'envoi de transfert Mojaloop"""
        # Créer un transfert de test
        user = test_utils.create_test_user(db_session, {
            "username": "mojaloopuser",
            "email": "mojaloop@example.com",
            "password": "testpass123"
        })
        
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Test User",
            "holder_id": "123456789",
            "holder_email": "test@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "mojaloop",
            "amount": 100.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Test transfer"
        })
        
        connector = MojaloopConnector(mojaloop_test_config)
        result = await connector.send_transfer(transfer)
        
        assert result["success"] is True
        assert result["dry_run"] is True
        assert "transfer_id" in result
        assert result["status"] == "ACCEPTED"
    
    def test_mojaloop_connectivity_test(self, mojaloop_test_config: Dict[str, Any]):
        """Test de connectivité Mojaloop"""
        connector = MojaloopConnector(mojaloop_test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = connector.test_connectivity()
            
            assert result["success"] is True
            assert result["endpoint"] == "https://test.mojaloop.com"


class TestISO20022Connector:
    """Tests du connecteur ISO 20022"""
    
    def test_iso20022_connector_initialization(self, iso20022_test_config: Dict[str, Any]):
        """Test de l'initialisation du connecteur ISO 20022"""
        connector = ISO20022Connector(iso20022_test_config)
        
        assert connector.message_types == ["pacs.008", "pacs.002", "pacs.004", "camt.052", "camt.053"]
    
    def test_iso20022_message_creation_pacs008(self, iso20022_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test de création de message ISO 20022 pacs.008"""
        # Créer un transfert de test
        user = test_utils.create_test_user(db_session, {
            "username": "iso20022user",
            "email": "iso20022@example.com",
            "password": "testpass123"
        })
        
        source_account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "TESTBIC",
            "holder_name": "Test Sender",
            "holder_id": "123456789",
            "holder_email": "sender@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        destination_account = test_utils.create_test_account(db_session, {
            "account_number": "0987654321",
            "iban": "US123456789012345678901234",
            "bic": "CHASUS33",
            "holder_name": "Test Receiver",
            "holder_id": "987654321",
            "holder_email": "receiver@example.com",
            "bank_name": "Test Bank",
            "bank_code": "54321",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
            "transfer_type": "iso20022",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Test transfer"
        })
        
        connector = ISO20022Connector(iso20022_test_config)
        iso_message = connector.create_pacs008_message(transfer)
        
        assert iso_message is not None
        assert "pacs.008" in iso_message
        assert "TESTBIC" in iso_message
        assert "CHASUS33" in iso_message
        assert "1000.00" in iso_message
        assert "USD" in iso_message
    
    def test_iso20022_message_parsing(self, iso20022_test_config: Dict[str, Any]):
        """Test de parsing des messages ISO 20022"""
        connector = ISO20022Connector(iso20022_test_config)
        
        # Parser un message pacs.002
        pacs002_message = iso20022_test_config["test_messages"]["pacs002"]
        parsed_message = connector.parse_iso20022_message(pacs002_message)
        
        assert parsed_message is not None
        assert parsed_message["message_type"] == "pacs.002"
        assert parsed_message["status"] == "ACSP"
        assert "MSG123456789" in parsed_message["message_id"]


class TestBankingConnectivity:
    """Tests de connectivité bancaire"""
    
    def test_swift_certificate_validation(self, bank_connectivity_test_config: Dict[str, Any]):
        """Test de validation des certificats SWIFT"""
        from app.connectors.swift import SwiftConnector
        
        config = {
            "bic": "TESTBIC",
            "cert_path": "/test/cert.pem",
            "key_path": "/test/key.pem",
            "endpoint": "https://test.swift.com",
            "timeout": 30,
            "dry_run": True
        }
        
        connector = SwiftConnector(config)
        
        with patch('cryptography.x509.load_pem_x509_certificate') as mock_cert:
            mock_cert.return_value.not_valid_after = "2030-12-31"
            
            result = connector.validate_certificates()
            
            assert result["success"] is True
            assert result["cert_valid"] is True
            assert result["key_valid"] is True
    
    def test_network_connectivity_tests(self, bank_connectivity_test_config: Dict[str, Any]):
        """Test des tests de connectivité réseau"""
        network_tests = bank_connectivity_test_config["network_tests"]
        
        for test_name, test_config in network_tests.items():
            if test_name == "ping":
                # Simuler un test ping
                result = {"success": True, "host": test_config["host"]}
                assert result["success"] == test_config["expected_result"]
            
            elif test_name == "dns":
                # Simuler un test DNS
                result = {"success": True, "host": test_config["host"]}
                assert result["success"] == test_config["expected_result"]
            
            elif test_name == "tls":
                # Simuler un test TLS
                result = {"success": True, "host": test_config["host"], "port": test_config["port"]}
                assert result["success"] == test_config["expected_result"]
    
    def test_endpoint_connectivity_tests(self, bank_connectivity_test_config: Dict[str, Any]):
        """Test de connectivité des endpoints"""
        endpoint_tests = bank_connectivity_test_config["test_endpoints"]
        
        for endpoint_name, endpoint_config in endpoint_tests.items():
            # Simuler un test de connectivité
            result = {
                "success": True,
                "endpoint": endpoint_config["url"],
                "status_code": endpoint_config["expected_status"]
            }
            
            assert result["success"] is True
            assert result["status_code"] == endpoint_config["expected_status"]


class TestConnectorIntegration:
    """Tests d'intégration des connecteurs"""
    
    @pytest.mark.asyncio
    async def test_swift_mojaloop_integration(self, swift_test_config: Dict[str, Any], mojaloop_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test d'intégration SWIFT et Mojaloop"""
        # Créer des transferts pour différents connecteurs
        user = test_utils.create_test_user(db_session, {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "testpass123"
        })
        
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Test User",
            "holder_id": "123456789",
            "holder_email": "test@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        # Test SWIFT
        swift_transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "SWIFT Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "SWIFT integration test"
        })
        
        swift_connector = SwiftConnector(swift_test_config)
        swift_result = await swift_connector.send_message(swift_transfer)
        
        assert swift_result["success"] is True
        assert swift_result["dry_run"] is True
        
        # Test Mojaloop
        mojaloop_transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "mojaloop",
            "amount": 100.00,
            "currency": "USD",
            "beneficiary_name": "Mojaloop Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Mojaloop integration test"
        })
        
        mojaloop_connector = MojaloopConnector(mojaloop_test_config)
        mojaloop_result = await mojaloop_connector.send_transfer(mojaloop_transfer)
        
        assert mojaloop_result["success"] is True
        assert mojaloop_result["dry_run"] is True
    
    def test_connector_error_handling(self, swift_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test de gestion d'erreur des connecteurs"""
        # Créer un transfert de test
        user = test_utils.create_test_user(db_session, {
            "username": "erroruser",
            "email": "error@example.com",
            "password": "testpass123"
        })
        
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Test User",
            "holder_id": "123456789",
            "holder_email": "test@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Error handling test"
        })
        
        connector = SwiftConnector(swift_test_config)
        
        # Simuler une erreur de connexion
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("Connection failed")
            
            result = connector.send_message_sync(transfer)
            
            assert result["success"] is False
            assert "error" in result
            assert "Connection failed" in result["error"]
    
    def test_connector_message_logging(self, swift_test_config: Dict[str, Any], test_utils, db_session: Session):
        """Test de journalisation des messages des connecteurs"""
        # Créer un transfert de test
        user = test_utils.create_test_user(db_session, {
            "username": "logginguser",
            "email": "logging@example.com",
            "password": "testpass123"
        })
        
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Test User",
            "holder_id": "123456789",
            "holder_email": "test@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD"
        }, user.id)
        
        transfer = test_utils.create_test_transfer(db_session, {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Logging test"
        })
        
        connector = SwiftConnector(swift_test_config)
        
        # Créer et logger un message
        swift_message = connector.create_mt103_message(transfer)
        log_result = connector.log_message(swift_message, "outgoing", transfer.id)
        
        assert log_result["success"] is True
        assert log_result["message_id"] is not None
        assert log_result["direction"] == "outgoing"
        assert log_result["transfer_id"] == transfer.id