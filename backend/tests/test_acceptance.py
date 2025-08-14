"""
Tests d'acceptation pour Banking Transfer Platform
Validation complète des fonctionnalités
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
import structlog

from app.connectors.swift_connector import (
    SWIFTConnector, 
    SWIFTConfig, 
    TransferRequest as SWIFTTransferRequest
)
from app.connectors.mojaloop_connector import (
    MojaloopConnector,
    MojaloopConfig,
    MojaloopTransferRequest
)

logger = structlog.get_logger(__name__)

class TestAcceptanceBankingTransfer:
    """Tests d'acceptation pour la plateforme de transferts bancaires"""
    
    @pytest.fixture
    async def swift_connector(self):
        """Connecteur SWIFT pour les tests"""
        config = SWIFTConfig(
            bic="TESTUS33XXX",
            bank_name="Test Bank",
            country_code="US",
            dry_run=True
        )
        connector = SWIFTConnector(config)
        await connector.initialize()
        yield connector
        await connector.close()
    
    @pytest.fixture
    async def mojaloop_connector(self):
        """Connecteur Mojaloop pour les tests"""
        config = MojaloopConfig(
            dfsp_id="test-dfsp",
            dfsp_name="Test DFSP",
            currency="CDF",
            country_code="CD",
            dry_run=True
        )
        connector = MojaloopConnector(config)
        await connector.initialize()
        yield connector
        await connector.close()

    @pytest.mark.asyncio
    async def test_swift_transfer_acceptance(self, swift_connector):
        """Test d'acceptation transfert SWIFT"""
        logger.info("Début test d'acceptation SWIFT")
        
        # Préparation de la demande
        request = SWIFTTransferRequest(
            id="TEST-SWIFT-001",
            amount=50000.00,
            currency="USD",
            sender_bic="TESTUS33XXX",
            sender_iban="US12345678901234567890",
            sender_name="John Doe",
            recipient_bic="RECIPIENTXXX",
            recipient_iban="DE12345678901234567890",
            recipient_name="Jane Smith",
            purpose="Payment for services",
            reference="INV-2024-001",
            urgent=False
        )
        
        # Exécution du transfert
        response = await swift_connector.send_transfer(request)
        
        # Vérifications
        assert response.id == request.id
        assert response.status == "COMPLETED"
        assert response.ack_received is True
        assert response.ack_timestamp is not None
        assert response.swift_message_id.startswith("SWIFT")
        assert response.mt103_content is not None
        assert response.error_message is None
        
        logger.info("Test d'acceptation SWIFT réussi", 
                   transfer_id=response.id,
                   status=response.status)

    @pytest.mark.asyncio
    async def test_mojaloop_transfer_acceptance(self, mojaloop_connector):
        """Test d'acceptation transfert Mojaloop"""
        logger.info("Début test d'acceptation Mojaloop")
        
        # Préparation de la demande
        request = MojaloopTransferRequest(
            id="TEST-ML-001",
            amount=25000.00,
            currency="CDF",
            payer_msisdn="243999999999",
            payer_name="Alice Johnson",
            payee_msisdn="243888888888",
            payee_name="Bob Wilson",
            purpose="Mobile money transfer",
            reference="MM-2024-001",
            urgent=False
        )
        
        # Exécution du transfert
        response = await mojaloop_connector.send_transfer(request)
        
        # Vérifications
        assert response.id == request.id
        assert response.status == "COMPLETED"
        assert response.settlement_completed is True
        assert response.settlement_timestamp is not None
        assert response.mojaloop_transaction_id.startswith("ML")
        assert response.quote_id.startswith("Q")
        assert response.transfer_id.startswith("T")
        assert response.error_message is None
        
        logger.info("Test d'acceptation Mojaloop réussi",
                   transfer_id=response.id,
                   status=response.status)

    @pytest.mark.asyncio
    async def test_swift_validation_acceptance(self, swift_connector):
        """Test d'acceptation validation SWIFT"""
        logger.info("Début test validation SWIFT")
        
        # Test avec IBAN invalide
        invalid_request = SWIFTTransferRequest(
            id="TEST-SWIFT-INVALID",
            amount=1000.00,
            currency="EUR",
            sender_bic="TESTUS33XXX",
            sender_iban="INVALID-IBAN",
            sender_name="Test User",
            recipient_bic="RECIPIENTXXX",
            recipient_iban="DE12345678901234567890",
            recipient_name="Test Recipient",
            purpose="Test validation",
            reference="TEST-001"
        )
        
        response = await swift_connector.send_transfer(invalid_request)
        
        # Vérifications
        assert response.status == "FAILED"
        assert "invalide" in response.error_message.lower()
        assert response.ack_received is False
        
        logger.info("Test validation SWIFT réussi", error=response.error_message)

    @pytest.mark.asyncio
    async def test_mojaloop_validation_acceptance(self, mojaloop_connector):
        """Test d'acceptation validation Mojaloop"""
        logger.info("Début test validation Mojaloop")
        
        # Test avec MSISDN invalide
        invalid_request = MojaloopTransferRequest(
            id="TEST-ML-INVALID",
            amount=1000.00,
            currency="CDF",
            payer_msisdn="123",  # MSISDN invalide
            payer_name="Test User",
            payee_msisdn="243888888888",
            payee_name="Test Recipient",
            purpose="Test validation",
            reference="TEST-001"
        )
        
        response = await mojaloop_connector.send_transfer(invalid_request)
        
        # Vérifications
        assert response.status == "FAILED"
        assert "invalide" in response.error_message.lower()
        assert response.settlement_completed is False
        
        logger.info("Test validation Mojaloop réussi", error=response.error_message)

    @pytest.mark.asyncio
    async def test_swift_iso20022_acceptance(self, swift_connector):
        """Test d'acceptation génération ISO 20022"""
        logger.info("Début test ISO 20022")
        
        request = SWIFTTransferRequest(
            id="TEST-ISO-001",
            amount=75000.00,
            currency="EUR",
            sender_bic="TESTUS33XXX",
            sender_iban="FR123456789012345678901234",
            sender_name="Pierre Dupont",
            recipient_bic="DEUTDEFFXXX",
            recipient_iban="DE12345678901234567890",
            recipient_name="Hans Mueller",
            purpose="International payment",
            reference="INT-2024-001"
        )
        
        # Génération du message ISO 20022
        iso_message = swift_connector._generate_iso20022_message(request)
        
        # Vérifications
        assert iso_message is not None
        assert "Document" in iso_message
        assert "FIToFICstmrCdtTrf" in iso_message
        assert request.id in iso_message
        assert request.currency in iso_message
        assert str(request.amount) in iso_message
        assert request.sender_bic in iso_message
        assert request.recipient_bic in iso_message
        
        logger.info("Test ISO 20022 réussi", message_length=len(iso_message))

    @pytest.mark.asyncio
    async def test_mojaloop_quote_acceptance(self, mojaloop_connector):
        """Test d'acceptation quote Mojaloop"""
        logger.info("Début test quote Mojaloop")
        
        request = MojaloopTransferRequest(
            id="TEST-QUOTE-001",
            amount=15000.00,
            currency="CDF",
            payer_msisdn="243999999999",
            payer_name="Test Payer",
            payee_msisdn="243888888888",
            payee_name="Test Payee",
            purpose="Test quote",
            reference="QUOTE-001"
        )
        
        # Demande de quote
        quote_response = await mojaloop_connector._request_quote(request)
        
        # Vérifications
        assert quote_response['success'] is True
        assert 'quote_id' in quote_response
        assert quote_response['quote_id'] is not None
        
        logger.info("Test quote Mojaloop réussi", quote_id=quote_response['quote_id'])

    @pytest.mark.asyncio
    async def test_swift_mt103_acceptance(self, swift_connector):
        """Test d'acceptation génération MT103"""
        logger.info("Début test MT103")
        
        request = SWIFTTransferRequest(
            id="TEST-MT103-001",
            amount=100000.00,
            currency="USD",
            sender_bic="TESTUS33XXX",
            sender_iban="US12345678901234567890",
            sender_name="American Bank",
            recipient_bic="RECIPIENTXXX",
            recipient_iban="GB12345678901234567890",
            recipient_name="British Bank",
            purpose="SWIFT MT103 test",
            reference="MT103-001"
        )
        
        # Génération du message MT103
        mt103_content = swift_connector._generate_mt103_content(request)
        
        # Vérifications
        assert mt103_content is not None
        assert "MT103" in mt103_content
        assert request.currency in mt103_content
        assert str(request.amount) in mt103_content
        assert request.sender_iban in mt103_content
        assert request.recipient_iban in mt103_content
        assert request.sender_name in mt103_content
        assert request.recipient_name in mt103_content
        
        logger.info("Test MT103 réussi", content_length=len(mt103_content))

    @pytest.mark.asyncio
    async def test_iban_validation_acceptance(self):
        """Test d'acceptation validation IBAN"""
        logger.info("Début test validation IBAN")
        
        from app.connectors.swift_connector import IBANValidator
        validator = IBANValidator()
        
        # Tests IBAN valides
        valid_ibans = [
            "DE89370400440532013000",  # Allemagne
            "FR1420041010050500013M02606",  # France
            "GB29NWBK60161331926819",  # Royaume-Uni
            "US12345678901234567890"  # États-Unis (format)
        ]
        
        for iban in valid_ibans:
            assert validator.validate(iban) is True, f"IBAN valide rejeté: {iban}"
        
        # Tests IBAN invalides
        invalid_ibans = [
            "INVALID-IBAN",
            "123456789",
            "DE123",  # Trop court
            "DE8937040044053201300012345678901234567890"  # Trop long
        ]
        
        for iban in invalid_ibans:
            assert validator.validate(iban) is False, f"IBAN invalide accepté: {iban}"
        
        logger.info("Test validation IBAN réussi")

    @pytest.mark.asyncio
    async def test_bic_validation_acceptance(self):
        """Test d'acceptation validation BIC"""
        logger.info("Début test validation BIC")
        
        from app.connectors.swift_connector import BICValidator
        validator = BICValidator()
        
        # Tests BIC valides
        valid_bics = [
            "DEUTDEFF",  # 8 caractères
            "DEUTDEFFXXX",  # 11 caractères
            "TESTUS33",  # Format test
            "RECIPIENTXXX"  # Format test
        ]
        
        for bic in valid_bics:
            assert validator.validate(bic) is True, f"BIC valide rejeté: {bic}"
        
        # Tests BIC invalides
        invalid_bics = [
            "INVALID",
            "12345678",
            "TEST123",  # Format invalide
            "DEUTDEFFXXXX"  # Trop long
        ]
        
        for bic in invalid_bics:
            assert validator.validate(bic) is False, f"BIC invalide accepté: {bic}"
        
        logger.info("Test validation BIC réussi")

    @pytest.mark.asyncio
    async def test_msisdn_validation_acceptance(self):
        """Test d'acceptation validation MSISDN"""
        logger.info("Début test validation MSISDN")
        
        from app.connectors.mojaloop_connector import MSISDNValidator
        validator = MSISDNValidator()
        
        # Tests MSISDN valides (RDC)
        valid_msisdns = [
            "243999999999",  # Format international
            "0999999999",  # Format local
            "243888888888",
            "0888888888"
        ]
        
        for msisdn in valid_msisdns:
            assert validator.validate(msisdn) is True, f"MSISDN valide rejeté: {msisdn}"
        
        # Tests MSISDN invalides
        invalid_msisdns = [
            "123",  # Trop court
            "12345678901234567890",  # Trop long
            "invalid",
            "243123",  # Format invalide
            "123456789"  # Format invalide
        ]
        
        for msisdn in invalid_msisdns:
            assert validator.validate(msisdn) is False, f"MSISDN invalide accepté: {msisdn}"
        
        logger.info("Test validation MSISDN réussi")

    @pytest.mark.asyncio
    async def test_end_to_end_acceptance(self, swift_connector, mojaloop_connector):
        """Test d'acceptation end-to-end complet"""
        logger.info("Début test end-to-end")
        
        # Test SWIFT
        swift_request = SWIFTTransferRequest(
            id="E2E-SWIFT-001",
            amount=50000.00,
            currency="USD",
            sender_bic="TESTUS33XXX",
            sender_iban="US12345678901234567890",
            sender_name="E2E Test Sender",
            recipient_bic="RECIPIENTXXX",
            recipient_iban="DE12345678901234567890",
            recipient_name="E2E Test Recipient",
            purpose="End-to-end test",
            reference="E2E-001"
        )
        
        swift_response = await swift_connector.send_transfer(swift_request)
        assert swift_response.status == "COMPLETED"
        
        # Test Mojaloop
        mojaloop_request = MojaloopTransferRequest(
            id="E2E-ML-001",
            amount=25000.00,
            currency="CDF",
            payer_msisdn="243999999999",
            payer_name="E2E Test Payer",
            payee_msisdn="243888888888",
            payee_name="E2E Test Payee",
            purpose="End-to-end test",
            reference="E2E-002"
        )
        
        mojaloop_response = await mojaloop_connector.send_transfer(mojaloop_request)
        assert mojaloop_response.status == "COMPLETED"
        
        logger.info("Test end-to-end réussi",
                   swift_status=swift_response.status,
                   mojaloop_status=mojaloop_response.status)

if __name__ == "__main__":
    # Exécution des tests d'acceptation
    pytest.main([__file__, "-v", "--tb=short"])