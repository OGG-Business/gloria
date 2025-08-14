"""
Tests de conformité pour la plateforme de transferts bancaires
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.kyc.models import KYCDocument, DocumentType, DocumentStatus, KYCCheck, KYCCheckType, KYCCheckStatus
from app.transfers.models import Transfer, TransferStatus
from app.audit.models import AuditLog, AuditEventType


class TestKYCCompliance:
    """Tests de conformité KYC"""
    
    def test_kyc_document_requirements(self, client: TestClient, test_user, db_session: Session):
        """Test des exigences de documents KYC"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester les types de documents requis
        required_document_types = [
            DocumentType.IDENTITY_CARD,
            DocumentType.PASSPORT,
            DocumentType.DRIVERS_LICENSE
        ]
        
        for doc_type in required_document_types:
            # Créer un document KYC
            document_data = {
                "document_type": doc_type.value,
                "document_number": f"DOC{doc_type.value.upper()}123456",
                "issuing_country": "FR",
                "expiry_date": "2030-12-31",
                "file_path": f"/uploads/{doc_type.value}_test.pdf",
                "file_size": 1024,
                "mime_type": "application/pdf"
            }
            
            response = client.post("/kyc/documents", json=document_data, headers=headers)
            
            # Vérifier que le document est accepté
            assert response.status_code in [200, 201]
            
            # Vérifier que le document est enregistré en base
            document = db_session.query(KYCDocument).filter(
                KYCDocument.user_id == test_user.id,
                KYCDocument.document_type == doc_type
            ).first()
            
            assert document is not None
            assert document.document_type == doc_type
            assert document.status == DocumentStatus.PENDING
    
    def test_kyc_verification_process(self, client: TestClient, test_user, db_session: Session):
        """Test du processus de vérification KYC"""
        # Créer un document KYC
        document = KYCDocument(
            user_id=test_user.id,
            document_type=DocumentType.IDENTITY_CARD,
            document_number="ID123456789",
            issuing_country="FR",
            expiry_date="2030-12-31",
            file_path="/uploads/id_card.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status=DocumentStatus.PENDING
        )
        db_session.add(document)
        db_session.commit()
        
        # Simuler une vérification KYC
        verification_data = {
            "document_id": document.id,
            "check_type": KYCCheckType.IDENTITY_VERIFICATION.value,
            "verification_method": "document_scan",
            "verification_result": "verified",
            "verification_date": datetime.utcnow().isoformat(),
            "verifier_id": "system",
            "notes": "Document verified successfully"
        }
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/kyc/verifications", json=verification_data, headers=headers)
        
        # Vérifier que la vérification est enregistrée
        assert response.status_code in [200, 201]
        
        # Vérifier que le check KYC est créé
        kyc_check = db_session.query(KYCCheck).filter(
            KYCCheck.document_id == document.id,
            KYCCheck.check_type == KYCCheckType.IDENTITY_VERIFICATION
        ).first()
        
        assert kyc_check is not None
        assert kyc_check.status == KYCCheckStatus.VERIFIED
    
    def test_kyc_completion_requirements(self, client: TestClient, test_user, db_session: Session):
        """Test des exigences de complétion KYC"""
        # Créer les documents KYC requis
        required_documents = [
            (DocumentType.IDENTITY_CARD, "ID123456789"),
            (DocumentType.PASSPORT, "PASS123456789"),
            (DocumentType.DRIVERS_LICENSE, "DL123456789")
        ]
        
        for doc_type, doc_number in required_documents:
            document = KYCDocument(
                user_id=test_user.id,
                document_type=doc_type,
                document_number=doc_number,
                issuing_country="FR",
                expiry_date="2030-12-31",
                file_path=f"/uploads/{doc_type.value}.pdf",
                file_size=1024,
                mime_type="application/pdf",
                status=DocumentStatus.VERIFIED
            )
            db_session.add(document)
        
        db_session.commit()
        
        # Vérifier que le KYC est complet
        documents = db_session.query(KYCDocument).filter(
            KYCDocument.user_id == test_user.id,
            KYCDocument.status == DocumentStatus.VERIFIED
        ).all()
        
        assert len(documents) >= 3  # Au moins 3 documents vérifiés
        
        # Vérifier que l'utilisateur peut effectuer des transferts
        # (Cette logique dépendra de l'implémentation spécifique)


class TestAMLCompliance:
    """Tests de conformité AML"""
    
    def test_transfer_limit_enforcement(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test de l'application des limites de transfert"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester les limites de transfert
        transfer_limits = {
            "daily": 10000,
            "monthly": 50000,
            "yearly": 500000
        }
        
        # Créer un transfert qui dépasse la limite quotidienne
        large_transfer_data = {
            "source_account_id": test_account.id,
            "destination_account_id": test_account.id,
            "amount": 15000.00,  # Dépasse la limite quotidienne
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "AML test"
        }
        
        response = client.post("/transfers", json=large_transfer_data, headers=headers)
        
        # Le transfert devrait être rejeté ou nécessiter une approbation spéciale
        assert response.status_code in [400, 422, 403]
        
        # Créer un transfert dans les limites
        normal_transfer_data = {
            "source_account_id": test_account.id,
            "destination_account_id": test_account.id,
            "amount": 5000.00,  # Dans les limites
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Normal transfer"
        }
        
        response = client.post("/transfers", json=normal_transfer_data, headers=headers)
        
        # Le transfert devrait être accepté
        assert response.status_code in [200, 201]
    
    def test_sanctions_screening(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test du screening des sanctions"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester avec un nom qui pourrait être dans les listes de sanctions
        # (Utiliser des noms fictifs pour les tests)
        test_cases = [
            {
                "beneficiary_name": "John Doe",  # Nom normal
                "expected_result": "allowed"
            },
            {
                "beneficiary_name": "Test Sanctioned Person",  # Nom fictif pour test
                "expected_result": "blocked"
            }
        ]
        
        for test_case in test_cases:
            transfer_data = {
                "source_account_id": test_account.id,
                "destination_account_id": test_account.id,
                "amount": 1000.00,
                "currency": "USD",
                "beneficiary_name": test_case["beneficiary_name"],
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": "US123456789012345678901234",
                "beneficiary_bic": "CHASUS33",
                "purpose": "Sanctions test"
            }
            
            response = client.post("/transfers", json=transfer_data, headers=headers)
            
            if test_case["expected_result"] == "allowed":
                assert response.status_code in [200, 201]
            else:
                assert response.status_code in [400, 422, 403]
    
    def test_pep_screening(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test du screening des PEP (Personnes Politiquement Exposées)"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester avec des noms qui pourraient être des PEP
        test_cases = [
            {
                "beneficiary_name": "John Smith",  # Nom normal
                "expected_result": "allowed"
            },
            {
                "beneficiary_name": "Test PEP Person",  # Nom fictif pour test
                "expected_result": "enhanced_due_diligence"
            }
        ]
        
        for test_case in test_cases:
            transfer_data = {
                "source_account_id": test_account.id,
                "destination_account_id": test_account.id,
                "amount": 1000.00,
                "currency": "USD",
                "beneficiary_name": test_case["beneficiary_name"],
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": "US123456789012345678901234",
                "beneficiary_bic": "CHASUS33",
                "purpose": "PEP test"
            }
            
            response = client.post("/transfers", json=transfer_data, headers=headers)
            
            if test_case["expected_result"] == "allowed":
                assert response.status_code in [200, 201]
            else:
                # Pour les PEP, le transfert pourrait être autorisé mais avec une surveillance renforcée
                assert response.status_code in [200, 201, 400, 422]


class TestDataRetentionCompliance:
    """Tests de conformité de rétention des données"""
    
    def test_transaction_record_retention(self, db_session: Session, test_utils):
        """Test de rétention des enregistrements de transactions"""
        # Créer un utilisateur et des transferts
        user = test_utils.create_test_user(db_session, {
            "username": "retentionuser",
            "email": "retention@example.com",
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
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00,
            "status": "active"
        }, user.id)
        
        # Créer des transferts avec différentes dates
        transfer_dates = [
            datetime.utcnow() - timedelta(days=365),  # 1 an
            datetime.utcnow() - timedelta(days=2555),  # 7 ans
            datetime.utcnow() - timedelta(days=3650),  # 10 ans
        ]
        
        transfers = []
        for i, transfer_date in enumerate(transfer_dates):
            transfer = Transfer(
                source_account_id=account.id,
                destination_account_id=account.id,
                transfer_type="swift",
                amount=100.00 + i,
                currency="USD",
                beneficiary_name=f"Beneficiary {i}",
                beneficiary_bank="Test Bank",
                beneficiary_iban=f"US123456789012345678901{i:03d}",
                beneficiary_bic="CHASUS33",
                purpose=f"Retention test {i}",
                status=TransferStatus.COMPLETED,
                created_at=transfer_date
            )
            db_session.add(transfer)
            transfers.append(transfer)
        
        db_session.commit()
        
        # Vérifier que tous les transferts sont conservés (rétention de 7 ans)
        all_transfers = db_session.query(Transfer).filter(
            Transfer.source_account_id == account.id
        ).all()
        
        assert len(all_transfers) == 3
        
        # Simuler une purge des anciens enregistrements (plus de 7 ans)
        old_transfers = db_session.query(Transfer).filter(
            Transfer.created_at < datetime.utcnow() - timedelta(days=2555)
        ).all()
        
        # Les transferts de plus de 7 ans devraient être marqués pour suppression
        # mais pas encore supprimés (rétention de 7 ans)
        assert len(old_transfers) == 1
    
    def test_kyc_document_retention(self, db_session: Session, test_utils):
        """Test de rétention des documents KYC"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "kycretentionuser",
            "email": "kycretention@example.com",
            "password": "testpass123"
        })
        
        # Créer des documents KYC avec différentes dates
        document_dates = [
            datetime.utcnow() - timedelta(days=365),  # 1 an
            datetime.utcnow() - timedelta(days=1825),  # 5 ans
            datetime.utcnow() - timedelta(days=2190),  # 6 ans
        ]
        
        documents = []
        for i, doc_date in enumerate(document_dates):
            document = KYCDocument(
                user_id=user.id,
                document_type=DocumentType.IDENTITY_CARD,
                document_number=f"ID{i:06d}",
                issuing_country="FR",
                expiry_date="2030-12-31",
                file_path=f"/uploads/id_card_{i}.pdf",
                file_size=1024,
                mime_type="application/pdf",
                status=DocumentStatus.VERIFIED,
                created_at=doc_date
            )
            db_session.add(document)
            documents.append(document)
        
        db_session.commit()
        
        # Vérifier que tous les documents sont conservés (rétention de 5 ans)
        all_documents = db_session.query(KYCDocument).filter(
            KYCDocument.user_id == user.id
        ).all()
        
        assert len(all_documents) == 3
        
        # Simuler une purge des anciens documents (plus de 5 ans)
        old_documents = db_session.query(KYCDocument).filter(
            KYCDocument.created_at < datetime.utcnow() - timedelta(days=1825)
        ).all()
        
        # Les documents de plus de 5 ans devraient être marqués pour suppression
        assert len(old_documents) == 1
    
    def test_audit_log_retention(self, db_session: Session, test_utils):
        """Test de rétention des logs d'audit"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "auditretentionuser",
            "email": "auditretention@example.com",
            "password": "testpass123"
        })
        
        # Créer des logs d'audit avec différentes dates
        log_dates = [
            datetime.utcnow() - timedelta(days=365),  # 1 an
            datetime.utcnow() - timedelta(days=3650),  # 10 ans
            datetime.utcnow() - timedelta(days=4015),  # 11 ans
        ]
        
        audit_logs = []
        for i, log_date in enumerate(log_dates):
            audit_log = AuditLog(
                user_id=user.id,
                event_type=AuditEventType.USER_LOGIN,
                event_data={"ip_address": "192.168.1.1"},
                ip_address="192.168.1.1",
                user_agent="Test Agent",
                created_at=log_date
            )
            db_session.add(audit_log)
            audit_logs.append(audit_log)
        
        db_session.commit()
        
        # Vérifier que tous les logs sont conservés (rétention de 10 ans)
        all_logs = db_session.query(AuditLog).filter(
            AuditLog.user_id == user.id
        ).all()
        
        assert len(all_logs) == 3
        
        # Simuler une purge des anciens logs (plus de 10 ans)
        old_logs = db_session.query(AuditLog).filter(
            AuditLog.created_at < datetime.utcnow() - timedelta(days=3650)
        ).all()
        
        # Les logs de plus de 10 ans devraient être marqués pour suppression
        assert len(old_logs) == 1


class TestPrivacyCompliance:
    """Tests de conformité à la vie privée"""
    
    def test_gdpr_data_encryption(self, db_session: Session):
        """Test du chiffrement des données selon le GDPR"""
        from app.common.encryption import encrypt_data, decrypt_data
        
        # Données personnelles sensibles
        sensitive_data = {
            "email": "test@example.com",
            "phone": "+1234567890",
            "address": "123 Main St, City, Country",
            "nationality": "FR",
            "date_of_birth": "1990-01-01"
        }
        
        # Vérifier que toutes les données sensibles sont chiffrées
        for field, value in sensitive_data.items():
            encrypted = encrypt_data(value)
            assert encrypted != value
            assert isinstance(encrypted, str)
            
            # Vérifier que le déchiffrement fonctionne
            decrypted = decrypt_data(encrypted)
            assert decrypted == value
    
    def test_right_to_forget(self, client: TestClient, test_user, db_session: Session):
        """Test du droit à l'oubli (GDPR)"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Demander la suppression des données
        response = client.delete("/auth/me", headers=headers)
        
        # Vérifier que la demande est acceptée
        assert response.status_code in [200, 204]
        
        # Vérifier que les données sont anonymisées ou supprimées
        # (Cette logique dépendra de l'implémentation spécifique)
    
    def test_consent_management(self, client: TestClient, test_user, db_session: Session):
        """Test de la gestion du consentement"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester la gestion du consentement
        consent_data = {
            "marketing_emails": True,
            "sms_notifications": False,
            "data_sharing": True,
            "analytics": False
        }
        
        response = client.post("/auth/consent", json=consent_data, headers=headers)
        
        # Vérifier que le consentement est enregistré
        assert response.status_code in [200, 201]
        
        # Récupérer les préférences de consentement
        response = client.get("/auth/consent", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que les préférences sont correctement enregistrées
        assert data["marketing_emails"] == True
        assert data["sms_notifications"] == False
        assert data["data_sharing"] == True
        assert data["analytics"] == False


class TestRegulatoryReporting:
    """Tests de reporting réglementaire"""
    
    def test_transaction_reporting(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test du reporting des transactions"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer plusieurs transferts
        for i in range(5):
            transfer_data = {
                "source_account_id": test_account.id,
                "destination_account_id": test_account.id,
                "amount": 1000.00 + i * 100,
                "currency": "USD",
                "beneficiary_name": f"Beneficiary {i}",
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": f"US123456789012345678901{i:03d}",
                "beneficiary_bic": "CHASUS33",
                "purpose": f"Reporting test {i}"
            }
            
            response = client.post("/transfers", json=transfer_data, headers=headers)
            assert response.status_code in [200, 201]
        
        # Générer un rapport de transactions
        report_data = {
            "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "report_type": "transaction_summary"
        }
        
        response = client.post("/admin/reports/transactions", json=report_data, headers=headers)
        
        # Vérifier que le rapport est généré
        assert response.status_code in [200, 201]
        
        # Vérifier le contenu du rapport
        data = response.json()
        assert "transactions" in data
        assert "summary" in data
        assert "total_amount" in data["summary"]
        assert "total_count" in data["summary"]
    
    def test_kyc_reporting(self, client: TestClient, test_user, db_session: Session):
        """Test du reporting KYC"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Générer un rapport KYC
        report_data = {
            "start_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "report_type": "kyc_status"
        }
        
        response = client.post("/admin/reports/kyc", json=report_data, headers=headers)
        
        # Vérifier que le rapport est généré
        assert response.status_code in [200, 201]
        
        # Vérifier le contenu du rapport
        data = response.json()
        assert "kyc_records" in data
        assert "summary" in data
        assert "pending_verifications" in data["summary"]
        assert "completed_verifications" in data["summary"]
    
    def test_aml_reporting(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test du reporting AML"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Générer un rapport AML
        report_data = {
            "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "report_type": "suspicious_activity"
        }
        
        response = client.post("/admin/reports/aml", json=report_data, headers=headers)
        
        # Vérifier que le rapport est généré
        assert response.status_code in [200, 201]
        
        # Vérifier le contenu du rapport
        data = response.json()
        assert "suspicious_activities" in data
        assert "summary" in data
        assert "total_alerts" in data["summary"]
        assert "investigated_cases" in data["summary"]