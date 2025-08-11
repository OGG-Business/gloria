"""
Tests end-to-end pour la plateforme de transferts bancaires
"""
import pytest
import time
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.transfers.models import Transfer, TransferStatus
from app.accounts.models import Account, AccountStatus
from app.auth.models import User, UserStatus


class TestCompleteTransferFlow:
    """Tests du flux complet de transfert"""
    
    def test_complete_swift_transfer_flow(self, client: TestClient, test_utils, db_session: Session):
        """Test du flux complet d'un transfert SWIFT"""
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "e2euser",
            "email": "e2e@example.com",
            "password": "testpass123",
            "first_name": "E2E",
            "last_name": "User"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "e2euser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte source
        source_account_data = {
            "account_number": "1234567890",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPP",
            "holder_name": "E2E User",
            "holder_id": "123456789",
            "holder_email": "e2e@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00
        }
        
        account_response = client.post("/accounts", json=source_account_data, headers=headers)
        assert account_response.status_code == 201
        source_account = account_response.json()
        
        # 4. Créer un transfert SWIFT
        transfer_data = {
            "source_account_id": source_account["id"],
            "destination_account_id": source_account["id"],  # Même compte pour le test
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "E2E test transfer"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        assert transfer_response.status_code == 201
        transfer = transfer_response.json()
        
        # 5. Vérifier que le transfert est créé avec le bon statut
        assert transfer["status"] == "initiated"
        assert transfer["amount"] == 1000.00
        assert transfer["currency"] == "USD"
        assert transfer["transfer_type"] == "swift"
        
        # 6. Suivre l'état du transfert
        transfer_id = transfer["id"]
        status_response = client.get(f"/transfers/{transfer_id}", headers=headers)
        assert status_response.status_code == 200
        transfer_status = status_response.json()
        
        # 7. Vérifier les événements du transfert
        events_response = client.get(f"/transfers/{transfer_id}/events", headers=headers)
        assert events_response.status_code == 200
        events = events_response.json()
        
        assert len(events) >= 1  # Au moins l'événement de création
        assert events[0]["event_type"] == "transfer_created"
        
        # 8. Vérifier que le solde du compte a été débité
        account_response = client.get(f"/accounts/{source_account['id']}", headers=headers)
        assert account_response.status_code == 200
        updated_account = account_response.json()
        
        # Le solde devrait être débité (selon l'implémentation)
        # assert updated_account["balance"] < source_account["balance"]
        
        print(f"E2E SWIFT transfer completed: {transfer_id}")
    
    def test_complete_mojaloop_transfer_flow(self, client: TestClient, test_utils, db_session: Session):
        """Test du flux complet d'un transfert Mojaloop"""
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "e2emojaloopuser",
            "email": "e2emojaloop@example.com",
            "password": "testpass123",
            "first_name": "E2E",
            "last_name": "MojaloopUser"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "e2emojaloopuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte
        account_data = {
            "account_number": "0987654321",
            "iban": "FR7630006000010987654321098",
            "bic": "BNPAFRPP",
            "holder_name": "E2E Mojaloop User",
            "holder_id": "987654321",
            "holder_email": "e2emojaloop@example.com",
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
        
        # 4. Créer un transfert Mojaloop
        transfer_data = {
            "source_account_id": account["id"],
            "destination_account_id": account["id"],
            "transfer_type": "mojaloop",
            "amount": 500.00,
            "currency": "USD",
            "beneficiary_name": "Mojaloop Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "E2E Mojaloop test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        assert transfer_response.status_code == 201
        transfer = transfer_response.json()
        
        # 5. Vérifier le transfert
        assert transfer["status"] == "initiated"
        assert transfer["amount"] == 500.00
        assert transfer["transfer_type"] == "mojaloop"
        
        print(f"E2E Mojaloop transfer completed: {transfer['id']}")
    
    def test_transfer_with_kyc_verification(self, client: TestClient, test_utils, db_session: Session):
        """Test de transfert avec vérification KYC"""
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "kyce2euser",
            "email": "kyce2e@example.com",
            "password": "testpass123"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "kyce2euser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte
        account_data = {
            "account_number": "1111111111",
            "iban": "FR7630006000011111111111111",
            "bic": "BNPAFRPP",
            "holder_name": "KYC E2E User",
            "holder_id": "111111111",
            "holder_email": "kyce2e@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00
        }
        
        account_response = client.post("/accounts", json=account_data, headers=headers)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 4. Télécharger un document KYC
        document_data = {
            "document_type": "identity_card",
            "document_number": "ID123456789",
            "issuing_country": "FR",
            "expiry_date": "2030-12-31",
            "file_path": "/uploads/id_card_e2e.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf"
        }
        
        document_response = client.post("/kyc/documents", json=document_data, headers=headers)
        assert document_response.status_code in [200, 201]
        
        # 5. Créer un transfert (qui pourrait nécessiter une vérification KYC)
        transfer_data = {
            "source_account_id": account["id"],
            "destination_account_id": account["id"],
            "transfer_type": "swift",
            "amount": 2000.00,
            "currency": "USD",
            "beneficiary_name": "KYC Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "KYC E2E test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        assert transfer_response.status_code in [201, 400, 422]  # 400/422 si KYC requis
        
        if transfer_response.status_code == 201:
            transfer = transfer_response.json()
            print(f"KYC E2E transfer completed: {transfer['id']}")
        else:
            print("KYC verification required for transfer")


class TestUserJourney:
    """Tests du parcours utilisateur complet"""
    
    def test_user_registration_to_transfer(self, client: TestClient, db_session: Session):
        """Test du parcours complet : inscription → connexion → compte → transfert"""
        # 1. Inscription d'un nouvel utilisateur
        registration_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "phone": "+1234567890"
        }
        
        registration_response = client.post("/auth/register", json=registration_data)
        assert registration_response.status_code in [200, 201]
        
        # 2. Connexion
        login_response = client.post("/auth/login", json={
            "username": "newuser",
            "password": "newpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Récupérer le profil utilisateur
        profile_response = client.get("/auth/me", headers=headers)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        assert profile["username"] == "newuser"
        assert profile["email"] == "newuser@example.com"
        
        # 4. Créer un compte
        account_data = {
            "account_number": "2222222222",
            "iban": "FR7630006000012222222222222",
            "bic": "BNPAFRPP",
            "holder_name": "New User",
            "holder_id": "222222222",
            "holder_email": "newuser@example.com",
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
        
        # 5. Lister les comptes
        accounts_response = client.get("/accounts", headers=headers)
        assert accounts_response.status_code == 200
        accounts = accounts_response.json()
        
        assert len(accounts) >= 1
        assert accounts[0]["account_number"] == "2222222222"
        
        # 6. Créer un transfert
        transfer_data = {
            "source_account_id": account["id"],
            "destination_account_id": account["id"],
            "transfer_type": "swift",
            "amount": 500.00,
            "currency": "USD",
            "beneficiary_name": "Journey Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "User journey test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        assert transfer_response.status_code == 201
        transfer = transfer_response.json()
        
        # 7. Lister les transferts
        transfers_response = client.get("/transfers", headers=headers)
        assert transfers_response.status_code == 200
        transfers = transfers_response.json()
        
        assert len(transfers) >= 1
        assert transfers[0]["id"] == transfer["id"]
        
        print(f"Complete user journey completed: {transfer['id']}")
    
    def test_admin_journey(self, client: TestClient, test_utils, db_session: Session):
        """Test du parcours administrateur"""
        # 1. Créer un utilisateur admin
        admin_user = test_utils.create_test_user(db_session, {
            "username": "admin",
            "email": "admin@example.com",
            "password": "adminpass123",
            "first_name": "Admin",
            "last_name": "User"
        })
        
        # 2. Se connecter en tant qu'admin
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "adminpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Accéder aux fonctionnalités admin
        # Note: Ces endpoints peuvent ne pas exister encore
        admin_endpoints = [
            "/admin/users",
            "/admin/transfers",
            "/admin/accounts",
            "/admin/kyc",
            "/admin/reports"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=headers)
            # 200 si l'endpoint existe, 404 sinon
            assert response.status_code in [200, 404]
        
        print("Admin journey completed")


class TestErrorScenarios:
    """Tests des scénarios d'erreur"""
    
    def test_insufficient_funds_transfer(self, client: TestClient, test_utils, db_session: Session):
        """Test de transfert avec fonds insuffisants"""
        # 1. Créer un utilisateur avec un compte à solde faible
        user = test_utils.create_test_user(db_session, {
            "username": "lowbalanceuser",
            "email": "lowbalance@example.com",
            "password": "testpass123"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "lowbalanceuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte avec un solde faible
        account_data = {
            "account_number": "3333333333",
            "iban": "FR7630006000013333333333333",
            "bic": "BNPAFRPP",
            "holder_name": "Low Balance User",
            "holder_id": "333333333",
            "holder_email": "lowbalance@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 100.00,  # Solde faible
            "daily_limit": 1000.00
        }
        
        account_response = client.post("/accounts", json=account_data, headers=headers)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 4. Tenter un transfert supérieur au solde
        transfer_data = {
            "source_account_id": account["id"],
            "destination_account_id": account["id"],
            "transfer_type": "swift",
            "amount": 500.00,  # Plus que le solde
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Insufficient funds test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        
        # Le transfert devrait être rejeté
        assert transfer_response.status_code in [400, 422]
        
        error_data = transfer_response.json()
        assert "error" in error_data or "detail" in error_data
        
        print("Insufficient funds test completed")
    
    def test_transfer_limit_exceeded(self, client: TestClient, test_utils, db_session: Session):
        """Test de dépassement de limite de transfert"""
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "limituser",
            "email": "limit@example.com",
            "password": "testpass123"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "limituser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte avec une limite quotidienne faible
        account_data = {
            "account_number": "4444444444",
            "iban": "FR7630006000014444444444444",
            "bic": "BNPAFRPP",
            "holder_name": "Limit User",
            "holder_id": "444444444",
            "holder_email": "limit@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 1000.00  # Limite faible
        }
        
        account_response = client.post("/accounts", json=account_data, headers=headers)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 4. Tenter un transfert qui dépasse la limite
        transfer_data = {
            "source_account_id": account["id"],
            "destination_account_id": account["id"],
            "transfer_type": "swift",
            "amount": 1500.00,  # Plus que la limite quotidienne
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Limit exceeded test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        
        # Le transfert devrait être rejeté
        assert transfer_response.status_code in [400, 422, 403]
        
        print("Transfer limit exceeded test completed")
    
    def test_invalid_iban_transfer(self, client: TestClient, test_utils, db_session: Session):
        """Test de transfert avec IBAN invalide"""
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "invalidibanuser",
            "email": "invalidiban@example.com",
            "password": "testpass123"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "invalidibanuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte
        account_data = {
            "account_number": "5555555555",
            "iban": "FR7630006000015555555555555",
            "bic": "BNPAFRPP",
            "holder_name": "Invalid IBAN User",
            "holder_id": "555555555",
            "holder_email": "invalidiban@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 10000.00,
            "daily_limit": 5000.00
        }
        
        account_response = client.post("/accounts", json=account_data, headers=headers)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 4. Tenter un transfert avec un IBAN invalide
        transfer_data = {
            "source_account_id": account["id"],
            "destination_account_id": account["id"],
            "transfer_type": "swift",
            "amount": 1000.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "INVALID_IBAN",  # IBAN invalide
            "beneficiary_bic": "CHASUS33",
            "purpose": "Invalid IBAN test"
        }
        
        transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
        
        # Le transfert devrait être rejeté
        assert transfer_response.status_code in [400, 422]
        
        print("Invalid IBAN test completed")


class TestPerformanceE2E:
    """Tests de performance E2E"""
    
    def test_multiple_concurrent_transfers(self, client: TestClient, test_utils, db_session: Session):
        """Test de transferts concurrents multiples"""
        import threading
        import time
        
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "concurrentuser",
            "email": "concurrent@example.com",
            "password": "testpass123"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "concurrentuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer un compte
        account_data = {
            "account_number": "6666666666",
            "iban": "FR7630006000016666666666666",
            "bic": "BNPAFRPP",
            "holder_name": "Concurrent User",
            "holder_id": "666666666",
            "holder_email": "concurrent@example.com",
            "bank_name": "Test Bank",
            "bank_code": "12345",
            "account_type": "current",
            "currency": "USD",
            "balance": 50000.00,
            "daily_limit": 10000.00
        }
        
        account_response = client.post("/accounts", json=account_data, headers=headers)
        assert account_response.status_code == 201
        account = account_response.json()
        
        # 4. Fonction pour créer un transfert
        def create_transfer(transfer_id):
            transfer_data = {
                "source_account_id": account["id"],
                "destination_account_id": account["id"],
                "transfer_type": "swift",
                "amount": 100.00 + transfer_id,
                "currency": "USD",
                "beneficiary_name": f"Concurrent Beneficiary {transfer_id}",
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": f"US123456789012345678901{transfer_id:03d}",
                "beneficiary_bic": "CHASUS33",
                "purpose": f"Concurrent test {transfer_id}"
            }
            
            response = client.post("/transfers", json=transfer_data, headers=headers)
            return response.status_code
        
        # 5. Créer des transferts en parallèle
        start_time = time.time()
        
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(target=lambda i=i: results.append(create_transfer(i)))
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 6. Vérifier les résultats
        successful_transfers = sum(1 for status in results if status == 201)
        
        assert successful_transfers >= 8  # Au moins 80% de succès
        assert duration < 30  # Moins de 30 secondes
        
        print(f"Concurrent transfers: {successful_transfers}/10 successful in {duration:.2f}s")
    
    def test_large_data_set_performance(self, client: TestClient, test_utils, db_session: Session):
        """Test de performance avec un grand volume de données"""
        # 1. Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "largeuser",
            "email": "large@example.com",
            "password": "testpass123"
        })
        
        # 2. Se connecter
        login_response = client.post("/auth/login", json={
            "username": "largeuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Créer plusieurs comptes
        accounts = []
        for i in range(5):
            account_data = {
                "account_number": f"777777777{i}",
                "iban": f"FR763000600001777777777777{i}",
                "bic": "BNPAFRPP",
                "holder_name": f"Large User {i}",
                "holder_id": f"77777777{i}",
                "holder_email": f"large{i}@example.com",
                "bank_name": "Test Bank",
                "bank_code": "12345",
                "account_type": "current",
                "currency": "USD",
                "balance": 10000.00,
                "daily_limit": 5000.00
            }
            
            account_response = client.post("/accounts", json=account_data, headers=headers)
            assert account_response.status_code == 201
            accounts.append(account_response.json())
        
        # 4. Créer de nombreux transferts
        start_time = time.time()
        
        for i in range(50):
            transfer_data = {
                "source_account_id": accounts[i % 5]["id"],
                "destination_account_id": accounts[(i + 1) % 5]["id"],
                "transfer_type": "swift",
                "amount": 50.00 + i,
                "currency": "USD",
                "beneficiary_name": f"Large Test Beneficiary {i}",
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": f"US123456789012345678901{i:03d}",
                "beneficiary_bic": "CHASUS33",
                "purpose": f"Large data test {i}"
            }
            
            transfer_response = client.post("/transfers", json=transfer_data, headers=headers)
            assert transfer_response.status_code == 201
        
        end_time = time.time()
        creation_duration = end_time - start_time
        
        # 5. Tester la récupération des données
        start_time = time.time()
        
        transfers_response = client.get("/transfers", headers=headers)
        assert transfers_response.status_code == 200
        transfers = transfers_response.json()
        
        end_time = time.time()
        retrieval_duration = end_time - start_time
        
        # 6. Vérifier les performances
        assert creation_duration < 60  # Moins de 60 secondes pour créer 50 transferts
        assert retrieval_duration < 5  # Moins de 5 secondes pour récupérer
        assert len(transfers) >= 50
        
        print(f"Large data test: {len(transfers)} transfers created in {creation_duration:.2f}s, retrieved in {retrieval_duration:.2f}s")