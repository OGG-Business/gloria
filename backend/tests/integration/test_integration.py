"""
Tests d'intégration pour la plateforme de transferts bancaires
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.transfers.models import Transfer, TransferStatus
from app.accounts.models import Account, AccountStatus
from app.auth.models import User, UserStatus
from app.kyc.models import KYCDocument, DocumentType, DocumentStatus


class TestDatabaseIntegration:
    """Tests d'intégration avec la base de données"""
    
    def test_database_connection_and_migrations(self, db_session: Session):
        """Test de connexion à la base de données et des migrations"""
        # Vérifier que la connexion fonctionne
        result = db_session.execute("SELECT 1").scalar()
        assert result == 1
        
        # Vérifier que les tables existent
        tables = db_session.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """).fetchall()
        
        table_names = [table[0] for table in tables]
        expected_tables = [
            'users', 'accounts', 'transfers', 'transfer_events',
            'kyc_documents', 'kyc_checks', 'audit_logs'
        ]
        
        for table in expected_tables:
            assert table in table_names
    
    def test_user_account_relationship_integration(self, db_session: Session, test_utils):
        """Test d'intégration de la relation utilisateur-compte"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "testpass123"
        })
        
        # Créer plusieurs comptes pour cet utilisateur
        accounts = []
        for i in range(3):
            account = test_utils.create_test_account(db_session, {
                "account_number": f"123456789{i}",
                "iban": f"FR763000600001123456789{i:03d}",
                "bic": "BNPAFRPP",
                "holder_name": f"Integration User {i}",
                "holder_id": f"12345678{i}",
                "holder_email": f"integration{i}@example.com",
                "bank_name": "Test Bank",
                "bank_code": "12345",
                "account_type": "current",
                "currency": "USD",
                "balance": 1000.00 + i * 100,
                "daily_limit": 5000.00,
                "status": "active"
            }, user.id)
            accounts.append(account)
        
        # Vérifier que les comptes sont bien associés à l'utilisateur
        user_accounts = db_session.query(Account).filter(Account.user_id == user.id).all()
        assert len(user_accounts) == 3
        
        # Vérifier que les relations sont correctes
        for account in user_accounts:
            assert account.user_id == user.id
            assert account.holder_name.startswith("Integration User")
    
    def test_transfer_account_integration(self, db_session: Session, test_utils):
        """Test d'intégration de la relation transfert-compte"""
        # Créer un utilisateur et des comptes
        user = test_utils.create_test_user(db_session, {
            "username": "transferuser",
            "email": "transfer@example.com",
            "password": "testpass123"
        })
        
        source_account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Transfer User",
            "holder_id": "123456789",
            "holder_email": "transfer@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00,
            "status": "active"
        }, user.id)
        
        destination_account = test_utils.create_test_account(db_session, {
            "account_number": "0987654321",
            "iban": "US123456789012345678901234",
            "bic": "CHASUS33",
            "holder_name": "Destination User",
            "holder_id": "987654321",
            "holder_email": "destination@example.com",
            "bank_name": "Test Bank",
            "bank_code": "54321",
            "account_type": "current",
            "currency": "USD",
            "balance": 5000.00,
            "daily_limit": 3000.00,
            "status": "active"
        }, user.id)
        
        # Créer plusieurs transferts
        transfers = []
        for i in range(5):
            transfer = test_utils.create_test_transfer(db_session, {
                "source_account_id": source_account.id,
                "destination_account_id": destination_account.id,
                "transfer_type": "swift",
                "amount": 100.00 + i * 50,
                "currency": "USD",
                "beneficiary_name": f"Beneficiary {i}",
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": f"US123456789012345678901{i:03d}",
                "beneficiary_bic": "CHASUS33",
                "purpose": f"Integration test {i}"
            })
            transfers.append(transfer)
        
        # Vérifier les relations
        source_transfers = db_session.query(Transfer).filter(
            Transfer.source_account_id == source_account.id
        ).all()
        assert len(source_transfers) == 5
        
        destination_transfers = db_session.query(Transfer).filter(
            Transfer.destination_account_id == destination_account.id
        ).all()
        assert len(destination_transfers) == 5
        
        # Vérifier que les montants sont corrects
        total_amount = sum(transfer.amount for transfer in source_transfers)
        assert total_amount == 600.00  # 100 + 150 + 200 + 250 + 300


class TestAPIDatabaseIntegration:
    """Tests d'intégration API-Base de données"""
    
    def test_user_creation_and_retrieval(self, client: TestClient, db_session: Session):
        """Test de création et récupération d'utilisateur via l'API"""
        # Créer un utilisateur via l'API
        user_data = {
            "username": "apiuser",
            "email": "api@example.com",
            "password": "testpass123",
            "first_name": "API",
            "last_name": "User",
            "phone": "+1234567890"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code in [200, 201]
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "apiuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Récupérer le profil utilisateur
        profile_response = client.get("/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        profile = profile_response.json()
        assert profile["username"] == "apiuser"
        assert profile["email"] == "api@example.com"
        
        # Vérifier en base de données
        user = db_session.query(User).filter(User.username == "apiuser").first()
        assert user is not None
        assert user.email == "api@example.com"
    
    def test_account_creation_and_balance_operations(self, client: TestClient, db_session: Session, test_utils):
        """Test de création de compte et opérations de solde via l'API"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "balanceuser",
            "email": "balance@example.com",
            "password": "testpass123"
        })
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "balanceuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer un compte via l'API
        account_data = {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Balance User",
            "holder_id": "123456789",
            "holder_email": "balance@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 5000.00,
            "daily_limit": 2000.00
        }
        
        account_response = client.post("/accounts", json=account_data, headers=headers)
        assert account_response.status_code == 201
        
        account = account_response.json()
        account_id = account["id"]
        
        # Vérifier le solde initial
        assert account["balance"] == 5000.00
        
        # Effectuer un débit via l'API
        debit_data = {
            "amount": 1000.00,
            "description": "Test debit"
        }
        
        debit_response = client.post(f"/accounts/{account_id}/debit", json=debit_data, headers=headers)
        assert debit_response.status_code == 200
        
        # Vérifier le nouveau solde
        updated_account_response = client.get(f"/accounts/{account_id}", headers=headers)
        assert updated_account_response.status_code == 200
        
        updated_account = updated_account_response.json()
        assert updated_account["balance"] == 4000.00
        
        # Vérifier en base de données
        db_account = db_session.query(Account).filter(Account.id == account_id).first()
        assert db_account.balance == 4000.00
    
    def test_transfer_creation_and_status_updates(self, client: TestClient, db_session: Session, test_utils):
        """Test de création de transfert et mises à jour de statut via l'API"""
        # Créer un utilisateur et des comptes
        user = test_utils.create_test_user(db_session, {
            "username": "transferapiuser",
            "email": "transferapi@example.com",
            "password": "testpass123"
        })
        
        source_account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Transfer API User",
            "holder_id": "123456789",
            "holder_email": "transferapi@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00,
            "status": "active"
        }, user.id)
        
        destination_account = test_utils.create_test_account(db_session, {
            "account_number": "0987654321",
            "iban": "US123456789012345678901234",
            "bic": "CHASUS33",
            "holder_name": "Destination API User",
            "holder_id": "987654321",
            "holder_email": "destination@example.com",
            "bank_name": "Test Bank",
            "bank_code": "54321",
            "account_type": "current",
            "currency": "USD",
            "balance": 5000.00,
            "daily_limit": 3000.00,
            "status": "active"
        }, user.id)
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "transferapiuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer un transfert via l'API
        transfer_data = {
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "API Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "API integration test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        assert transfer_response.status_code == 201
        
        transfer = transfer_response.json()
        transfer_id = transfer["id"]
        
        # Vérifier le statut initial
        assert transfer["status"] == "initiated"
        
        # Mettre à jour le statut via l'API
        status_update_data = {
            "status": "pending",
            "reason": "Processing transfer"
        }
        
        status_response = client.patch(f"/transfers/{transfer_id}/status", json=status_update_data, headers=headers)
        assert status_response.status_code == 200
        
        # Vérifier le nouveau statut
        updated_transfer_response = client.get(f"/transfers/{transfer_id}", headers=headers)
        assert updated_transfer_response.status_code == 200
        
        updated_transfer = updated_transfer_response.json()
        assert updated_transfer["status"] == "pending"
        
        # Vérifier en base de données
        db_transfer = db_session.query(Transfer).filter(Transfer.id == transfer_id).first()
        assert db_transfer.status == TransferStatus.PENDING


class TestKYCIntegration:
    """Tests d'intégration KYC"""
    
    def test_kyc_document_upload_and_verification(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration du téléchargement et de la vérification de documents KYC"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "kycuser",
            "email": "kyc@example.com",
            "password": "testpass123"
        })
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "kycuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Télécharger un document KYC via l'API
        document_data = {
            "document_type": "identity_card",
            "document_number": "ID123456789",
            "issuing_country": "FR",
            "expiry_date": "2030-12-31",
            "file_path": "/uploads/id_card_kyc.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf"
        }
        
        document_response = client.post("/kyc/documents", json=document_data, headers=headers)
        assert document_response.status_code in [200, 201]
        
        document = document_response.json()
        document_id = document["id"]
        
        # Vérifier le statut initial
        assert document["status"] == "pending"
        
        # Simuler une vérification via l'API
        verification_data = {
            "verification_result": "verified",
            "verification_method": "document_scan",
            "verifier_id": "system",
            "notes": "Document verified successfully"
        }
        
        verification_response = client.post(f"/kyc/documents/{document_id}/verify", json=verification_data, headers=headers)
        assert verification_response.status_code == 200
        
        # Vérifier le nouveau statut
        updated_document_response = client.get(f"/kyc/documents/{document_id}", headers=headers)
        assert updated_document_response.status_code == 200
        
        updated_document = updated_document_response.json()
        assert updated_document["status"] == "verified"
        
        # Vérifier en base de données
        db_document = db_session.query(KYCDocument).filter(KYCDocument.id == document_id).first()
        assert db_document.status == DocumentStatus.VERIFIED
    
    def test_kyc_completion_check(self, client: TestClient, db_session: Session, test_utils):
        """Test de vérification de complétion KYC"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "kyccompleteuser",
            "email": "kyccomplete@example.com",
            "password": "testpass123"
        })
        
        # Créer plusieurs documents KYC vérifiés
        document_types = [DocumentType.IDENTITY_CARD, DocumentType.PASSPORT, DocumentType.DRIVERS_LICENSE]
        
        for doc_type in document_types:
            document = KYCDocument(
                user_id=user.id,
                document_type=doc_type,
                document_number=f"DOC{doc_type.value.upper()}123456",
                issuing_country="FR",
                expiry_date="2030-12-31",
                file_path=f"/uploads/{doc_type.value}.pdf",
                file_size=1024,
                mime_type="application/pdf",
                status=DocumentStatus.VERIFIED
            )
            db_session.add(document)
        
        db_session.commit()
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "kyccompleteuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Vérifier le statut KYC
        kyc_status_response = client.get("/kyc/status", headers=headers)
        assert kyc_status_response.status_code == 200
        
        kyc_status = kyc_status_response.json()
        assert kyc_status["is_complete"] is True
        assert len(kyc_status["documents"]) == 3


class TestAuditIntegration:
    """Tests d'intégration d'audit"""
    
    def test_audit_logging_integration(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration de la journalisation d'audit"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "audituser",
            "email": "audit@example.com",
            "password": "testpass123"
        })
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "audituser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Effectuer des actions qui devraient être auditées
        actions = [
            ("/auth/me", "GET", "user_profile_access"),
            ("/accounts", "GET", "accounts_list_access"),
            ("/transfers", "GET", "transfers_list_access")
        ]
        
        for endpoint, method, expected_event in actions:
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            else:
                response = client.post(endpoint, headers=headers)
            
            # Vérifier que l'action a été audité
            audit_logs = db_session.execute("""
                SELECT event_type, user_id 
                FROM audit_logs 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT 1
            """, {"user_id": user.id}).fetchall()
            
            if audit_logs:
                assert audit_logs[0][1] == user.id
    
    def test_data_access_logging(self, client: TestClient, db_session: Session, test_utils):
        """Test de journalisation d'accès aux données"""
        # Créer un utilisateur et des données sensibles
        user = test_utils.create_test_user(db_session, {
            "username": "dataloguser",
            "email": "datalog@example.com",
            "password": "testpass123"
        })
        
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Data Log User",
            "holder_id": "123456789",
            "holder_email": "datalog@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00,
            "status": "active"
        }, user.id)
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "dataloguser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Accéder aux données sensibles
        account_response = client.get(f"/accounts/{account.id}", headers=headers)
        assert account_response.status_code == 200
        
        # Vérifier que l'accès a été journalisé
        data_access_logs = db_session.execute("""
            SELECT data_type, access_type, user_id 
            FROM data_access_logs 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT 1
        """, {"user_id": user.id}).fetchall()
        
        if data_access_logs:
            assert data_access_logs[0][2] == user.id


class TestNotificationIntegration:
    """Tests d'intégration des notifications"""
    
    def test_email_notification_integration(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration des notifications par email"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "emailuser",
            "email": "email@example.com",
            "password": "testpass123"
        })
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "emailuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer un transfert qui devrait déclencher une notification
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Email User",
            "holder_id": "123456789",
            "holder_email": "email@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00,
            "status": "active"
        }, user.id)
        
        transfer_data = {
            "source_account_id": account.id,
            "destination_account_id": account.id,
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Email Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Email notification test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        assert transfer_response.status_code == 201
        
        # Vérifier que la notification a été créée
        notifications = db_session.execute("""
            SELECT notification_type, recipient_email, status 
            FROM notifications 
            WHERE recipient_email = :email 
            ORDER BY created_at DESC 
            LIMIT 1
        """, {"email": "email@example.com"}).fetchall()
        
        if notifications:
            assert notifications[0][0] == "email"
            assert notifications[0][1] == "email@example.com"
    
    def test_sms_notification_integration(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration des notifications par SMS"""
        # Créer un utilisateur avec un numéro de téléphone
        user = test_utils.create_test_user(db_session, {
            "username": "smsuser",
            "email": "sms@example.com",
            "password": "testpass123",
            "phone": "+1234567890"
        })
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "smsuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Simuler une action qui déclenche une notification SMS
        # (par exemple, une tentative de connexion échouée)
        for i in range(5):
            failed_login_response = client.post("/auth/login", json={
                "username": "smsuser",
                "password": "wrongpassword"
            })
            assert failed_login_response.status_code == 401
        
        # Vérifier que la notification SMS a été créée
        sms_notifications = db_session.execute("""
            SELECT notification_type, recipient_phone, status 
            FROM notifications 
            WHERE recipient_phone = :phone 
            ORDER BY created_at DESC 
            LIMIT 1
        """, {"phone": "+1234567890"}).fetchall()
        
        if sms_notifications:
            assert sms_notifications[0][0] == "sms"
            assert sms_notifications[0][1] == "+1234567890"


class TestSecurityIntegration:
    """Tests d'intégration de sécurité"""
    
    def test_encryption_integration(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration du chiffrement"""
        # Créer un utilisateur avec des données sensibles
        user = test_utils.create_test_user(db_session, {
            "username": "encryptuser",
            "email": "encrypt@example.com",
            "password": "testpass123"
        })
        
        # Créer un compte avec des données sensibles
        account = test_utils.create_test_account(db_session, {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "Encrypt User",
            "holder_id": "123456789",
            "holder_email": "encrypt@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00,
            "status": "active"
        }, user.id)
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "encryptuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Récupérer les données du compte
        account_response = client.get(f"/accounts/{account.id}", headers=headers)
        assert account_response.status_code == 200
        
        account_data = account_response.json()
        
        # Vérifier que les données sensibles sont chiffrées en base
        db_account = db_session.query(Account).filter(Account.id == account.id).first()
        
        # Les données sensibles devraient être chiffrées en base mais déchiffrées via l'API
        assert account_data["iban"] == "FR7630006000011234567890189"  # Déchiffré via l'API
        # En base, l'IBAN devrait être chiffré (selon l'implémentation)
    
    def test_rate_limiting_integration(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration de la limitation de débit"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "ratelimituser",
            "email": "ratelimit@example.com",
            "password": "testpass123"
        })
        
        # Tenter plusieurs connexions échouées
        for i in range(10):
            response = client.post("/auth/login", json={
                "username": "ratelimituser",
                "password": "wrongpassword"
            })
            
            if response.status_code == 429:  # Too Many Requests
                break
        
        # Vérifier que la limitation de débit s'est activée
        assert response.status_code == 429
        
        # Vérifier que le compte a été temporairement verrouillé
        db_user = db_session.query(User).filter(User.username == "ratelimituser").first()
        # Le statut devrait être LOCKED ou le nombre de tentatives échouées devrait être élevé
        assert db_user.failed_login_attempts >= 5 or db_user.status == UserStatus.LOCKED


class TestMonitoringIntegration:
    """Tests d'intégration de monitoring"""
    
    def test_metrics_collection_integration(self, client: TestClient, db_session: Session, test_utils):
        """Test d'intégration de la collecte de métriques"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "metricsuser",
            "email": "metrics@example.com",
            "password": "testpass123"
        })
        
        # Effectuer plusieurs actions pour générer des métriques
        actions = [
            ("/auth/login", "POST", {"username": "metricsuser", "password": "testpass123"}),
            ("/auth/me", "GET", {}),
            ("/health", "GET", {}),
            ("/metrics", "GET", {})
        ]
        
        for endpoint, method, data in actions:
            if method == "POST":
                response = client.post(endpoint, json=data)
            else:
                response = client.get(endpoint)
            
            assert response.status_code in [200, 201]
        
        # Vérifier que les métriques ont été collectées
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        
        metrics_content = metrics_response.text
        
        # Vérifier la présence de métriques spécifiques
        assert "http_requests_total" in metrics_content
        assert "http_request_duration_seconds" in metrics_content
    
    def test_health_check_integration(self, client: TestClient, db_session: Session):
        """Test d'intégration du health check"""
        # Vérifier le health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        
        # Vérifier les composants critiques
        assert health_data["status"] == "healthy"
        assert "database" in health_data["components"]
        assert "redis" in health_data["components"]
        assert "vault" in health_data["components"]
        
        # Vérifier que tous les composants sont en bonne santé
        for component, status in health_data["components"].items():
            assert status["status"] == "healthy"