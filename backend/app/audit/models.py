"""
Modèles d'audit pour la traçabilité complète
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base


class AuditEventType(str, enum.Enum):
    """Types d'événements d'audit"""
    # Authentification
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    
    # Comptes
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_UPDATED = "account_updated"
    ACCOUNT_SUSPENDED = "account_suspended"
    ACCOUNT_ACTIVATED = "account_activated"
    BALANCE_CHANGED = "balance_changed"
    
    # Transferts
    TRANSFER_INITIATED = "transfer_initiated"
    TRANSFER_APPROVED = "transfer_approved"
    TRANSFER_REJECTED = "transfer_rejected"
    TRANSFER_CANCELLED = "transfer_cancelled"
    TRANSFER_COMPLETED = "transfer_completed"
    TRANSFER_FAILED = "transfer_failed"
    
    # KYC
    KYC_DOCUMENT_UPLOADED = "kyc_document_uploaded"
    KYC_DOCUMENT_APPROVED = "kyc_document_approved"
    KYC_DOCUMENT_REJECTED = "kyc_document_rejected"
    KYC_CHECK_INITIATED = "kyc_check_initiated"
    KYC_CHECK_COMPLETED = "kyc_check_completed"
    SANCTIONS_MATCH_FOUND = "sanctions_match_found"
    PEP_MATCH_FOUND = "pep_match_found"
    
    # Administration
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    POLICY_UPDATED = "policy_updated"
    
    # Système
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BACKUP_CREATED = "backup_created"
    MAINTENANCE_STARTED = "maintenance_started"
    MAINTENANCE_COMPLETED = "maintenance_completed"
    SECURITY_ALERT = "security_alert"


class AuditSeverity(str, enum.Enum):
    """Niveaux de sévérité des événements d'audit"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """Logs d'audit principaux"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    event_type = Column(Enum(AuditEventType), nullable=False)
    severity = Column(Enum(AuditSeverity), nullable=False, default=AuditSeverity.INFO)
    
    # Utilisateur et session
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Contexte
    resource_type = Column(String(50), nullable=True)  # user, account, transfer, etc.
    resource_id = Column(String(100), nullable=True)  # ID de la ressource affectée
    action = Column(String(100), nullable=False)  # create, update, delete, etc.
    
    # Données
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Données détaillées de l'événement
    before_state = Column(JSON, nullable=True)  # État avant modification
    after_state = Column(JSON, nullable=True)  # État après modification
    
    # Contexte technique
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    trace_id = Column(String(100), nullable=True)  # ID de traçage distribué
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', user_id={self.user_id})>"


class SecurityEvent(Base):
    """Événements de sécurité"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Type d'événement
    event_type = Column(String(100), nullable=False)  # brute_force, suspicious_activity, etc.
    severity = Column(Enum(AuditSeverity), nullable=False)
    
    # Contexte
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    
    # Détails
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Actions prises
    action_taken = Column(String(100), nullable=True)  # block_ip, lock_account, etc.
    automated = Column(Boolean, default=True)
    
    # Résolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, event_type='{self.event_type}', severity='{self.severity}')>"


class DataAccessLog(Base):
    """Logs d'accès aux données sensibles"""
    __tablename__ = "data_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Utilisateur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Données consultées
    data_type = Column(String(50), nullable=False)  # personal_info, financial_data, etc.
    record_id = Column(String(100), nullable=True)  # ID de l'enregistrement consulté
    
    # Accès
    access_type = Column(String(50), nullable=False)  # view, export, print, etc.
    access_method = Column(String(50), nullable=False)  # api, web, mobile, etc.
    
    # Contexte
    purpose = Column(String(255), nullable=True)  # Raison de l'accès
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")
    
    def __repr__(self):
        return f"<DataAccessLog(id={self.id}, user_id={self.user_id}, data_type='{self.data_type}')>"


class ComplianceReport(Base):
    """Rapports de conformité"""
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations du rapport
    report_type = Column(String(100), nullable=False)  # kyc, aml, audit, etc.
    report_period = Column(String(50), nullable=False)  # daily, weekly, monthly, etc.
    report_date = Column(DateTime, nullable=False)
    
    # Contenu
    summary = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Statut
    status = Column(String(50), nullable=False, default="generated")  # generated, reviewed, approved
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Fichier
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<ComplianceReport(id={self.id}, type='{self.report_type}', date='{self.report_date}')>"


class AuditPolicy(Base):
    """Politiques d'audit configurables"""
    __tablename__ = "audit_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    events_to_log = Column(JSON, nullable=True)  # Liste des événements à logger
    retention_period_days = Column(Integer, nullable=False, default=2555)  # 7 ans par défaut
    alert_thresholds = Column(JSON, nullable=True)  # Seuils d'alerte
    
    # Filtres
    include_ips = Column(JSON, nullable=True)  # IPs à inclure
    exclude_ips = Column(JSON, nullable=True)  # IPs à exclure
    include_users = Column(JSON, nullable=True)  # Utilisateurs à inclure
    exclude_users = Column(JSON, nullable=True)  # Utilisateurs à exclure
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AuditPolicy(id={self.id}, name='{self.name}')>"