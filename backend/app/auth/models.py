"""
Modèles d'authentification et d'utilisateurs
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base


class UserStatus(str, enum.Enum):
    """Statuts des utilisateurs"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserRole(str, enum.Enum):
    """Rôles des utilisateurs"""
    ADMIN = "admin"
    USER = "user"
    OPERATOR = "operator"
    AUDITOR = "auditor"


class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Informations personnelles
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    nationality = Column(String(3), nullable=True)  # Code pays ISO
    
    # Authentification
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION)
    
    # Sécurité
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relations
    accounts = relationship("Account", back_populates="user")
    roles = relationship("UserRole", back_populates="user")
    kyc_documents = relationship("KYCDocument", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_locked(self) -> bool:
        """Vérifie si le compte est verrouillé"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def has_role(self, role: UserRole) -> bool:
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return any(user_role.role == role for user_role in self.roles)
    
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est admin"""
        return self.has_role(UserRole.ADMIN)


class UserRole(Base):
    """Rôles des utilisateurs"""
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="roles")
    
    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role='{self.role}')>"


class RefreshToken(Base):
    """Tokens de rafraîchissement"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si le token est expiré"""
        return datetime.utcnow() > self.expires_at


class LoginAttempt(Base):
    """Tentatives de connexion"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=False)
    
    # Résultat
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<LoginAttempt(id={self.id}, username='{self.username}', success={self.success})>"


class PasswordReset(Base):
    """Demandes de réinitialisation de mot de passe"""
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    
    # Relations
    user = relationship("User")
    
    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la demande est expirée"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_used(self) -> bool:
        """Vérifie si la demande a été utilisée"""
        return self.used_at is not None


class Session(Base):
    """Sessions utilisateur"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Données de session
    data = Column(Text, nullable=True)  # JSON serialized
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User")
    
    def __repr__(self):
        return f"<Session(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la session est expirée"""
        return datetime.utcnow() > self.expires_at