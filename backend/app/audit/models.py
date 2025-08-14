"""
Audit models for Banking Transfer Platform
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base

class AuditSeverity(enum.Enum):
    """Audit severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    trace_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    resource = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed, pending
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, status={self.status})>"

class SecurityEvent(Base):
    """Security event model"""
    __tablename__ = "security_events"
    
    id = Column(String(36), primary_key=True)
    event_type = Column(String(100), nullable=False)  # login_failed, suspicious_activity, etc.
    severity = Column(Enum(AuditSeverity), default=AuditSeverity.INFO, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string for additional data
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"

class DataAccessLog(Base):
    """Data access log model"""
    __tablename__ = "data_access_logs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    data_type = Column(String(100), nullable=False)  # account, transfer, kyc, etc.
    data_id = Column(String(36), nullable=True)
    access_type = Column(String(50), nullable=False)  # read, write, delete
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DataAccessLog(id={self.id}, user_id={self.user_id}, data_type={self.data_type})>"

class ComplianceReport(Base):
    """Compliance report model"""
    __tablename__ = "compliance_reports"
    
    id = Column(String(36), primary_key=True)
    report_type = Column(String(100), nullable=False)  # kyc, aml, sanctions, etc.
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    generated_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, generated, delivered
    metadata = Column(Text, nullable=True)  # JSON string for report details
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ComplianceReport(id={self.id}, type={self.report_type}, period={self.period_start})>"

class AuditPolicy(Base):
    """Audit policy model"""
    __tablename__ = "audit_policies"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    retention_days = Column(Integer, default=2555, nullable=False)  # 7 years default
    log_level = Column(Enum(AuditSeverity), default=AuditSeverity.INFO, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<AuditPolicy(id={self.id}, name={self.name})>"