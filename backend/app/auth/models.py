"""
Authentication models for Banking Transfer Platform
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from passlib.hash import bcrypt

from app.common.database import BaseModel

class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    COMPLIANCE_OFFICER = "compliance_officer"
    FINANCE_OFFICER = "finance_officer"

class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    # Basic information
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Status and verification
    status = Column(String(20), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)
    
    # KYC and compliance
    kyc_status = Column(String(20), default="pending", nullable=False)
    kyc_level = Column(Integer, default=1, nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)
    
    # Security
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    roles = relationship("UserRoleAssignment", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    login_attempts = relationship("LoginAttempt", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = bcrypt.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return bcrypt.verify(password, self.password_hash)
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False
    
    def increment_failed_attempts(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None

class UserRoleAssignment(BaseModel):
    """User role assignment model"""
    __tablename__ = "user_role_assignments"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)
    assigned_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

class RefreshToken(BaseModel):
    """Refresh token model"""
    __tablename__ = "refresh_tokens"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    revoked_by_user = relationship("User", foreign_keys=[revoked_by])
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        return not self.revoked and not self.is_expired()

class LoginAttempt(BaseModel):
    """Login attempt model"""
    __tablename__ = "login_attempts"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    email = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="login_attempts")

class PasswordReset(BaseModel):
    """Password reset model"""
    __tablename__ = "password_resets"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        return not self.used and not self.is_expired()

class Session(BaseModel):
    """User session model"""
    __tablename__ = "sessions"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return self.active and not self.is_expired()