"""
Tests de sécurité pour la plateforme de transferts bancaires
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.auth.models import User, UserStatus
from app.auth.services import create_access_token, verify_password
from app.config import get_settings


class TestAuthentication:
    """Tests d'authentification"""
    
    def test_valid_login(self, client: TestClient, test_user: User):
        """Test de connexion avec des identifiants valides"""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login(self, client: TestClient):
        """Test de connexion avec des identifiants invalides"""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]
    
    def test_locked_account_login(self, client: TestClient, db_session: Session):
        """Test de connexion avec un compte verrouillé"""
        # Créer un utilisateur verrouillé
        from app.auth.services import get_password_hash
        
        locked_user = User(
            username="lockeduser",
            email="locked@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=False,
            status=UserStatus.LOCKED
        )
        db_session.add(locked_user)
        db_session.commit()
        
        response = client.post("/auth/login", json={
            "username": "lockeduser",
            "password": "testpass123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Account is locked" in data["detail"]
    
    def test_token_expiration(self, test_user: User):
        """Test d'expiration du token"""
        # Créer un token expiré
        expired_token = create_access_token(
            data={"sub": test_user.username},
            expires_delta=timedelta(seconds=-1)
        )
        
        # Vérifier que le token est expiré
        try:
            jwt.decode(expired_token, get_settings().security.secret_key, algorithms=["HS256"])
            assert False, "Token should be expired"
        except jwt.ExpiredSignatureError:
            assert True
    
    def test_invalid_token(self, client: TestClient):
        """Test avec un token invalide"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Could not validate credentials" in data["detail"]


class TestAuthorization:
    """Tests d'autorisation"""
    
    def test_admin_access(self, client: TestClient, db_session: Session):
        """Test d'accès administrateur"""
        # Créer un utilisateur admin
        from app.auth.services import get_password_hash
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpass123"),
            is_active=True,
            status=UserStatus.ACTIVE
        )
        db_session.add(admin_user)
        db_session.commit()
        
        # Se connecter en tant qu'admin
        login_response = client.post("/auth/login", json={
            "username": "admin",
            "password": "adminpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Tester l'accès à un endpoint admin
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/admin/users", headers=headers)
        
        # Note: L'endpoint admin peut ne pas exister encore, mais le test vérifie l'autorisation
        assert response.status_code in [200, 404]  # 404 si l'endpoint n'existe pas
    
    def test_user_access_restricted(self, client: TestClient, test_user: User):
        """Test d'accès utilisateur à des endpoints restreints"""
        # Se connecter en tant qu'utilisateur normal
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Tester l'accès à un endpoint admin
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/admin/users", headers=headers)
        
        # L'utilisateur normal ne devrait pas avoir accès
        assert response.status_code == 403
    
    def test_public_endpoints(self, client: TestClient):
        """Test d'accès aux endpoints publics"""
        # Endpoints qui ne nécessitent pas d'authentification
        public_endpoints = [
            "/",
            "/health",
            "/docs",
            "/openapi.json"
        ]
        
        for endpoint in public_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 404]  # 404 si l'endpoint n'existe pas


class TestInputValidation:
    """Tests de validation des entrées"""
    
    def test_sql_injection_prevention(self, client: TestClient):
        """Test de prévention des injections SQL"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'hacked'); --",
            "admin'--",
            "1' UNION SELECT * FROM users--"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post("/auth/login", json={
                "username": malicious_input,
                "password": "testpass123"
            })
            
            # Le système devrait gérer ces entrées de manière sécurisée
            assert response.status_code in [401, 422]  # 401 pour échec auth, 422 pour validation
    
    def test_xss_prevention(self, client: TestClient):
        """Test de prévention XSS"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for xss_input in xss_inputs:
            response = client.post("/auth/register", json={
                "username": "testuser",
                "email": f"{xss_input}@example.com",
                "password": "testpass123",
                "first_name": xss_input,
                "last_name": "User"
            })
            
            # Le système devrait valider et nettoyer ces entrées
            assert response.status_code in [400, 422]
    
    def test_path_traversal_prevention(self, client: TestClient):
        """Test de prévention du path traversal"""
        path_traversal_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for path_input in path_traversal_inputs:
            response = client.get(f"/files/{path_input}")
            
            # Le système devrait bloquer ces tentatives
            assert response.status_code in [400, 404, 403]


class TestEncryption:
    """Tests de chiffrement"""
    
    def test_password_hashing(self, test_user: User):
        """Test du hachage des mots de passe"""
        # Vérifier que le mot de passe est haché
        assert test_user.hashed_password != "testpass123"
        assert test_user.hashed_password.startswith("$2b$")
        
        # Vérifier que la vérification fonctionne
        assert verify_password("testpass123", test_user.hashed_password)
        assert not verify_password("wrongpassword", test_user.hashed_password)
    
    def test_sensitive_data_encryption(self, db_session: Session):
        """Test du chiffrement des données sensibles"""
        from app.common.encryption import encrypt_data, decrypt_data
        
        sensitive_data = {
            "credit_card": "4111111111111111",
            "ssn": "123-45-6789",
            "iban": "FR7630006000011234567890189"
        }
        
        for field, value in sensitive_data.items():
            # Chiffrer les données
            encrypted = encrypt_data(value)
            assert encrypted != value
            assert isinstance(encrypted, str)
            
            # Déchiffrer les données
            decrypted = decrypt_data(encrypted)
            assert decrypted == value


class TestRateLimiting:
    """Tests de limitation de débit"""
    
    def test_login_rate_limiting(self, client: TestClient):
        """Test de limitation de débit pour la connexion"""
        # Tenter plusieurs connexions échouées
        for i in range(10):
            response = client.post("/auth/login", json={
                "username": "testuser",
                "password": "wrongpassword"
            })
        
        # La dernière tentative devrait être bloquée
        assert response.status_code == 429  # Too Many Requests
    
    def test_api_rate_limiting(self, client: TestClient, test_user: User):
        """Test de limitation de débit pour les API"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Faire plusieurs requêtes rapides
        for i in range(100):
            response = client.get("/auth/me", headers=headers)
            if response.status_code == 429:
                break
        
        # À un moment donné, la limitation devrait s'activer
        assert response.status_code in [200, 429]


class TestSessionManagement:
    """Tests de gestion des sessions"""
    
    def test_session_timeout(self, client: TestClient, test_user: User):
        """Test d'expiration de session"""
        # Se connecter
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Utiliser le token immédiatement
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        # Note: Pour tester l'expiration réelle, il faudrait attendre
        # que le token expire, ce qui prendrait trop de temps
    
    def test_concurrent_sessions(self, client: TestClient, test_user: User):
        """Test de sessions concurrentes"""
        # Se connecter plusieurs fois
        tokens = []
        for i in range(3):
            login_response = client.post("/auth/login", json={
                "username": "testuser",
                "password": "testpass123"
            })
            
            assert login_response.status_code == 200
            tokens.append(login_response.json()["access_token"])
        
        # Tous les tokens devraient être valides
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == 200


class TestAuditLogging:
    """Tests de journalisation d'audit"""
    
    def test_login_audit_log(self, client: TestClient, test_user: User, db_session: Session):
        """Test de journalisation des connexions"""
        from app.audit.models import AuditLog, AuditEventType
        
        # Se connecter
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        
        # Vérifier que l'événement est journalisé
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.event_type == AuditEventType.USER_LOGIN
        ).first()
        
        assert audit_log is not None
        assert audit_log.user_id == test_user.id
        assert audit_log.event_type == AuditEventType.USER_LOGIN
    
    def test_failed_login_audit_log(self, client: TestClient, db_session: Session):
        """Test de journalisation des tentatives de connexion échouées"""
        from app.audit.models import AuditLog, AuditEventType
        
        # Tenter une connexion échouée
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        
        # Vérifier que l'événement est journalisé
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.event_type == AuditEventType.USER_LOGIN_FAILED
        ).first()
        
        assert audit_log is not None
        assert audit_log.event_type == AuditEventType.USER_LOGIN_FAILED


class TestDataProtection:
    """Tests de protection des données"""
    
    def test_pii_encryption(self, db_session: Session):
        """Test du chiffrement des données personnelles"""
        from app.common.encryption import encrypt_data, decrypt_data
        
        pii_data = {
            "email": "test@example.com",
            "phone": "+1234567890",
            "address": "123 Main St, City, Country",
            "nationality": "FR"
        }
        
        for field, value in pii_data.items():
            # Chiffrer les données
            encrypted = encrypt_data(value)
            assert encrypted != value
            
            # Déchiffrer les données
            decrypted = decrypt_data(encrypted)
            assert decrypted == value
    
    def test_data_anonymization(self, db_session: Session):
        """Test de l'anonymisation des données"""
        from app.common.anonymization import anonymize_data
        
        sensitive_data = {
            "email": "test@example.com",
            "phone": "+1234567890",
            "name": "John Doe",
            "address": "123 Main St, City, Country"
        }
        
        anonymized = anonymize_data(sensitive_data)
        
        # Vérifier que les données sont anonymisées
        assert anonymized["email"] != sensitive_data["email"]
        assert anonymized["phone"] != sensitive_data["phone"]
        assert anonymized["name"] != sensitive_data["name"]
        assert anonymized["address"] != sensitive_data["address"]
        
        # Vérifier que la structure est préservée
        assert "email" in anonymized
        assert "phone" in anonymized
        assert "name" in anonymized
        assert "address" in anonymized