"""
KYC models for Banking Transfer Platform
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base

class KYCStatus(enum.Enum):
    """KYC status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class DocumentType(enum.Enum):
    """Document types"""
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    PROOF_OF_ADDRESS = "proof_of_address"
    PROOF_OF_INCOME = "proof_of_income"

class KYCDocument(Base):
    """KYC document model"""
    __tablename__ = "kyc_documents"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(Enum(KYCStatus), default=KYCStatus.PENDING, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="kyc_documents")
    
    def __repr__(self):
        return f"<KYCDocument(id={self.id}, type={self.document_type}, status={self.status})>"

class KYCCheck(Base):
    """KYC check model"""
    __tablename__ = "kyc_checks"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    check_type = Column(String(50), nullable=False)  # sanctions, pep, aml, etc.
    status = Column(Enum(KYCStatus), default=KYCStatus.PENDING, nullable=False)
    result = Column(Text, nullable=True)  # JSON result
    risk_score = Column(Float, default=0.0, nullable=False)
    performed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<KYCCheck(id={self.id}, type={self.check_type}, status={self.status})>"

class SanctionsMatch(Base):
    """Sanctions match model"""
    __tablename__ = "sanctions_matches"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sanctions_list = Column(String(100), nullable=False)  # OFAC, UN, EU, etc.
    matched_name = Column(String(255), nullable=False)
    match_score = Column(Float, nullable=False)
    match_details = Column(Text, nullable=True)  # JSON details
    is_false_positive = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SanctionsMatch(id={self.id}, user_id={self.user_id}, score={self.match_score})>"

class PEPMatch(Base):
    """PEP match model"""
    __tablename__ = "pep_matches"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    pep_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=True)
    country = Column(String(3), nullable=True)
    match_score = Column(Float, nullable=False)
    match_details = Column(Text, nullable=True)  # JSON details
    is_false_positive = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PEPMatch(id={self.id}, user_id={self.user_id}, name={self.pep_name})>"

class KYCPolicy(Base):
    """KYC policy model"""
    __tablename__ = "kyc_policies"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    risk_threshold = Column(Float, default=0.7, nullable=False)
    auto_approve_below = Column(Float, default=0.3, nullable=False)
    auto_reject_above = Column(Float, default=0.8, nullable=False)
    requires_manual_review = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<KYCPolicy(id={self.id}, name={self.name})>"