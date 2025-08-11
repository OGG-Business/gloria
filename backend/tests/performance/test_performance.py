"""
Tests de performance pour la plateforme de transferts bancaires
"""
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.main import app
from app.transfers.models import Transfer, TransferStatus
from app.accounts.models import Account, AccountStatus
from app.auth.models import User


class TestLoadPerformance:
    """Tests de performance sous charge"""
    
    def test_concurrent_transfer_creation(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test de création concurrente de transferts"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Données de transfert
        transfer_data = {
            "source_account_id": test_account.id,
            "destination_account_id": test_account.id,
            "amount": 100.00,
            "currency": "USD",
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Performance test"
        }
        
        # Créer des transferts en parallèle
        def create_transfer():
            response = client.post("/transfers", json=transfer_data, headers=headers)
            return response.status_code
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: create_transfer(), range(50)))
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier les résultats
        successful_transfers = sum(1 for status in results if status == 200)
        
        assert successful_transfers >= 45  # Au moins 90% de succès
        assert duration < 30  # Moins de 30 secondes
        
        print(f"Created {successful_transfers}/50 transfers in {duration:.2f} seconds")
    
    def test_concurrent_user_login(self, client: TestClient, db_session: Session):
        """Test de connexion concurrente d'utilisateurs"""
        # Créer plusieurs utilisateurs de test
        from app.auth.services import get_password_hash
        
        users = []
        for i in range(20):
            user = {
                "username": f"testuser{i}",
                "email": f"test{i}@example.com",
                "password": "testpass123",
                "first_name": f"Test{i}",
                "last_name": "User"
            }
            
            # Créer l'utilisateur dans la base de données
            db_user = User(
                username=user["username"],
                email=user["email"],
                hashed_password=get_password_hash(user["password"]),
                first_name=user["first_name"],
                last_name=user["last_name"],
                is_active=True
            )
            db_session.add(db_user)
            users.append(user)
        
        db_session.commit()
        
        # Tester les connexions en parallèle
        def login_user(user_data):
            response = client.post("/auth/login", json={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            return response.status_code
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(login_user, users))
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier les résultats
        successful_logins = sum(1 for status in results if status == 200)
        
        assert successful_logins >= 18  # Au moins 90% de succès
        assert duration < 10  # Moins de 10 secondes
        
        print(f"Successful logins: {successful_logins}/20 in {duration:.2f} seconds")
    
    def test_database_query_performance(self, db_session: Session, test_utils):
        """Test de performance des requêtes de base de données"""
        # Créer des données de test
        user = test_utils.create_test_user(db_session, {
            "username": "perfuser",
            "email": "perf@example.com",
            "password": "testpass123"
        })
        
        # Créer plusieurs comptes
        accounts = []
        for i in range(100):
            account = test_utils.create_test_account(db_session, {
                "account_number": f"123456789{i:03d}",
                "iban": f"FR763000600001123456789{i:03d}",
                "bic": "BNPAFRPP",
                "holder_name": f"Test User {i}",
                "holder_id": f"123456789{i:03d}",
                "holder_email": f"user{i}@example.com",
                "bank_name": "Test Bank",
                "bank_code": "12345",
                "account_type": "current",
                "currency": "USD",
                "balance": 1000.00 + i,
                "daily_limit": 5000.00,
                "status": "active"
            }, user.id)
            accounts.append(account)
        
        # Créer plusieurs transferts
        transfers = []
        for i in range(500):
            transfer = test_utils.create_test_transfer(db_session, {
                "source_account_id": accounts[i % 100].id,
                "destination_account_id": accounts[(i + 1) % 100].id,
                "transfer_type": "swift",
                "amount": 100.00 + i,
                "currency": "USD",
                "beneficiary_name": f"Beneficiary {i}",
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": f"US123456789012345678901{i:03d}",
                "beneficiary_bic": "CHASUS33",
                "purpose": f"Transfer {i}"
            })
            transfers.append(transfer)
        
        # Test de requête simple
        start_time = time.time()
        accounts_query = db_session.query(Account).filter(Account.user_id == user.id).all()
        simple_query_time = time.time() - start_time
        
        assert len(accounts_query) == 100
        assert simple_query_time < 0.1  # Moins de 100ms
        
        # Test de requête avec jointure
        start_time = time.time()
        transfers_with_accounts = db_session.query(Transfer).join(Account).filter(
            Account.user_id == user.id
        ).all()
        join_query_time = time.time() - start_time
        
        assert len(transfers_with_accounts) == 500
        assert join_query_time < 0.5  # Moins de 500ms
        
        # Test de requête avec agrégation
        start_time = time.time()
        total_balance = db_session.query(Account).filter(
            Account.user_id == user.id
        ).with_entities(func.sum(Account.balance)).scalar()
        aggregate_query_time = time.time() - start_time
        
        assert total_balance > 0
        assert aggregate_query_time < 0.1  # Moins de 100ms
        
        print(f"Simple query: {simple_query_time:.3f}s")
        print(f"Join query: {join_query_time:.3f}s")
        print(f"Aggregate query: {aggregate_query_time:.3f}s")


class TestStressPerformance:
    """Tests de performance sous stress"""
    
    def test_high_concurrency_transfers(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test de transferts sous haute concurrence"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Données de transfert
        transfer_data = {
            "source_account_id": test_account.id,
            "destination_account_id": test_account.id,
            "amount": 10.00,
            "currency": "USD",
            "beneficiary_name": "Stress Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Stress test"
        }
        
        # Créer des transferts sous stress
        def create_transfer():
            response = client.post("/transfers", json=transfer_data, headers=headers)
            return response.status_code
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(lambda _: create_transfer(), range(200)))
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier les résultats
        successful_transfers = sum(1 for status in results if status == 200)
        error_transfers = sum(1 for status in results if status >= 400)
        
        assert successful_transfers >= 150  # Au moins 75% de succès
        assert duration < 60  # Moins de 60 secondes
        
        print(f"Stress test: {successful_transfers}/200 successful, {error_transfers} errors in {duration:.2f}s")
    
    def test_memory_usage_under_load(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test d'utilisation mémoire sous charge"""
        import psutil
        import os
        
        # Obtenir l'utilisation mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer de nombreux transferts
        transfer_data = {
            "source_account_id": test_account.id,
            "destination_account_id": test_account.id,
            "amount": 5.00,
            "currency": "USD",
            "beneficiary_name": "Memory Test Beneficiary",
            "beneficiary_bank": "Test Bank",
            "beneficiary_iban": "US123456789012345678901234",
            "beneficiary_bic": "CHASUS33",
            "purpose": "Memory test"
        }
        
        for i in range(1000):
            response = client.post("/transfers", json=transfer_data, headers=headers)
            if response.status_code != 200:
                break
        
        # Obtenir l'utilisation mémoire finale
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Vérifier que l'augmentation mémoire est raisonnable
        assert memory_increase < 100  # Moins de 100MB d'augmentation
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")


class TestEndurancePerformance:
    """Tests de performance d'endurance"""
    
    def test_long_running_operations(self, client: TestClient, test_user, test_account, db_session: Session):
        """Test d'opérations de longue durée"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Effectuer des opérations pendant une période prolongée
        start_time = time.time()
        operations_count = 0
        successful_operations = 0
        
        while time.time() - start_time < 300:  # 5 minutes
            # Créer un transfert
            transfer_data = {
                "source_account_id": test_account.id,
                "destination_account_id": test_account.id,
                "amount": 1.00,
                "currency": "USD",
                "beneficiary_name": "Endurance Test Beneficiary",
                "beneficiary_bank": "Test Bank",
                "beneficiary_iban": "US123456789012345678901234",
                "beneficiary_bic": "CHASUS33",
                "purpose": f"Endurance test {operations_count}"
            }
            
            response = client.post("/transfers", json=transfer_data, headers=headers)
            operations_count += 1
            
            if response.status_code == 200:
                successful_operations += 1
            
            # Petite pause pour éviter de surcharger
            time.sleep(0.1)
        
        # Vérifier les résultats
        success_rate = successful_operations / operations_count if operations_count > 0 else 0
        
        assert success_rate >= 0.8  # Au moins 80% de succès
        assert operations_count >= 100  # Au moins 100 opérations
        
        print(f"Endurance test: {successful_operations}/{operations_count} successful ({success_rate:.1%})")


class TestResponseTimePerformance:
    """Tests de temps de réponse"""
    
    def test_api_response_times(self, client: TestClient, test_user, test_account):
        """Test des temps de réponse des API"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester différents endpoints
        endpoints_to_test = [
            ("/auth/me", "GET"),
            ("/accounts", "GET"),
            ("/transfers", "GET"),
            ("/health", "GET")
        ]
        
        response_times = {}
        
        for endpoint, method in endpoints_to_test:
            times = []
            
            for _ in range(10):  # 10 requêtes par endpoint
                start_time = time.time()
                
                if method == "GET":
                    response = client.get(endpoint, headers=headers)
                else:
                    response = client.post(endpoint, headers=headers)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convertir en ms
                times.append(response_time)
                
                assert response.status_code in [200, 404]  # 404 si l'endpoint n'existe pas
            
            # Calculer les statistiques
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            response_times[endpoint] = {
                "avg": avg_time,
                "max": max_time,
                "min": min_time
            }
            
            # Vérifier les seuils de performance
            assert avg_time < 500  # Moins de 500ms en moyenne
            assert max_time < 2000  # Moins de 2s au maximum
        
        # Afficher les résultats
        for endpoint, stats in response_times.items():
            print(f"{endpoint}: avg={stats['avg']:.1f}ms, max={stats['max']:.1f}ms, min={stats['min']:.1f}ms")
    
    def test_database_response_times(self, db_session: Session, test_utils):
        """Test des temps de réponse de la base de données"""
        # Créer des données de test
        user = test_utils.create_test_user(db_session, {
            "username": "resptimeuser",
            "email": "resptime@example.com",
            "password": "testpass123"
        })
        
        # Créer plusieurs comptes
        for i in range(50):
            test_utils.create_test_account(db_session, {
                "account_number": f"123456789{i:03d}",
                "iban": f"FR763000600001123456789{i:03d}",
                "bic": "BNPAFRPP",
                "holder_name": f"Test User {i}",
                "holder_id": f"123456789{i:03d}",
                "holder_email": f"user{i}@example.com",
                "bank_name": "Test Bank",
                "bank_code": "12345",
                "account_type": "current",
                "currency": "USD",
                "balance": 1000.00,
                "daily_limit": 5000.00,
                "status": "active"
            }, user.id)
        
        # Tester différents types de requêtes
        query_times = {}
        
        # Requête simple
        start_time = time.time()
        accounts = db_session.query(Account).filter(Account.user_id == user.id).all()
        simple_time = (time.time() - start_time) * 1000
        
        query_times["simple"] = simple_time
        assert simple_time < 100  # Moins de 100ms
        
        # Requête avec tri
        start_time = time.time()
        sorted_accounts = db_session.query(Account).filter(
            Account.user_id == user.id
        ).order_by(Account.account_number).all()
        sort_time = (time.time() - start_time) * 1000
        
        query_times["sort"] = sort_time
        assert sort_time < 150  # Moins de 150ms
        
        # Requête avec pagination
        start_time = time.time()
        paginated_accounts = db_session.query(Account).filter(
            Account.user_id == user.id
        ).limit(10).offset(0).all()
        pagination_time = (time.time() - start_time) * 1000
        
        query_times["pagination"] = pagination_time
        assert pagination_time < 50  # Moins de 50ms
        
        # Afficher les résultats
        for query_type, response_time in query_times.items():
            print(f"Database {query_type} query: {response_time:.1f}ms")


class TestScalabilityPerformance:
    """Tests de scalabilité"""
    
    def test_scalability_with_data_volume(self, db_session: Session, test_utils):
        """Test de scalabilité avec le volume de données"""
        # Créer un utilisateur
        user = test_utils.create_test_user(db_session, {
            "username": "scalabilityuser",
            "email": "scalability@example.com",
            "password": "testpass123"
        })
        
        # Tester avec différents volumes de données
        data_volumes = [10, 100, 1000]
        
        for volume in data_volumes:
            # Créer des comptes
            start_time = time.time()
            
            for i in range(volume):
                test_utils.create_test_account(db_session, {
                    "account_number": f"123456789{i:06d}",
                    "iban": f"FR763000600001123456789{i:06d}",
                    "bic": "BNPAFRPP",
                    "holder_name": f"Test User {i}",
                    "holder_id": f"123456789{i:06d}",
                    "holder_email": f"user{i}@example.com",
                    "bank_name": "Test Bank",
                    "bank_code": "12345",
                    "account_type": "current",
                    "currency": "USD",
                    "balance": 1000.00,
                    "daily_limit": 5000.00,
                    "status": "active"
                }, user.id)
            
            creation_time = time.time() - start_time
            
            # Tester la requête
            start_time = time.time()
            accounts = db_session.query(Account).filter(Account.user_id == user.id).all()
            query_time = time.time() - start_time
            
            print(f"Volume {volume}: Creation={creation_time:.2f}s, Query={query_time:.3f}s")
            
            # Vérifier que les performances restent acceptables
            assert creation_time < volume * 0.01  # Moins de 10ms par compte
            assert query_time < volume * 0.001  # Moins de 1ms par compte
            assert len(accounts) == volume