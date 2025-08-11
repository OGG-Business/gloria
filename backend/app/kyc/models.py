"""
Modèles KYC/AML pour la conformité
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base


class DocumentType(str, enum.Enum):
    """Types de documents KYC"""
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    PROOF_OF_ADDRESS = "proof_of_address"
    PROOF_OF_INCOME = "proof_of_income"
    BUSINESS_LICENSE = "business_license"
    ARTICLES_OF_INCORPORATION = "articles_of_incorporation"


class DocumentStatus(str, enum.Enum):
    """Statuts des documents"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class KYCCheckType(str, enum.Enum):
    """Types de vérifications KYC"""
    IDENTITY_VERIFICATION = "identity_verification"
    ADDRESS_VERIFICATION = "address_verification"
    SANCTIONS_SCREENING = "sanctions_screening"
    PEP_SCREENING = "pep_screening"
    ADVERSE_MEDIA = "adverse_media"
    CREDIT_CHECK = "credit_check"


class KYCCheckStatus(str, enum.Enum):
    """Statuts des vérifications KYC"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


class RiskLevel(str, enum.Enum):
    """Niveaux de risque"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class KYCDocument(Base):
    """Documents KYC"""
    __tablename__ = "kyc_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Type et statut
    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING)
    
    # Informations du document
    document_number = Column(String(100), nullable=True)
    issuing_country = Column(String(3), nullable=True)  # Code pays ISO
    issuing_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Fichiers
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Vérification
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="kyc_documents")
    verifier = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<KYCDocument(id={self.id}, user_id={self.user_id}, type='{self.document_type}')>"
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si le document est expiré"""
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si le document est valide"""
        return self.status == DocumentStatus.APPROVED and not self.is_expired


class KYCCheck(Base):
    """Vérifications KYC"""
    __tablename__ = "kyc_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Type et statut
    check_type = Column(Enum(KYCCheckType), nullable=False)
    status = Column(Enum(KYCCheckStatus), nullable=False, default=KYCCheckStatus.PENDING)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    
    # Résultats
    score = Column(Float, nullable=True)  # Score de risque 0-100
    details = Column(JSON, nullable=True)  # Détails de la vérification
    flags = Column(JSON, nullable=True)  # Alertes détectées
    
    # Références externes
    external_check_id = Column(String(100), nullable=True)
    provider = Column(String(100), nullable=True)  # Fournisseur de vérification
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relations
    user = relationship("User")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<KYCCheck(id={self.id}, user_id={self.user_id}, type='{self.check_type}')>"
    
    @property
    def is_completed(self) -> bool:
        """Vérifie si la vérification est terminée"""
        return self.status in [KYCCheckStatus.PASSED, KYCCheckStatus.FAILED, KYCCheckStatus.MANUAL_REVIEW]


class SanctionsMatch(Base):
    """Correspondances avec les listes de sanctions"""
    __tablename__ = "sanctions_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations de la correspondance
    list_name = Column(String(255), nullable=False)  # Nom de la liste
    entity_name = Column(String(255), nullable=False)  # Nom de l'entité dans la liste
    match_score = Column(Float, nullable=False)  # Score de correspondance 0-100
    
    # Détails
    entity_type = Column(String(50), nullable=True)  # individual, organization, vessel, etc.
    country = Column(String(3), nullable=True)  # Code pays
    date_of_birth = Column(DateTime, nullable=True)
    nationality = Column(String(3), nullable=True)
    
    # Références
    external_id = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    
    # Statut
    is_false_positive = Column(Boolean, default=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<SanctionsMatch(id={self.id}, user_id={self.user_id}, list='{self.list_name}')>"


class PEPMatch(Base):
    """Correspondances avec les Personnes Politiquement Exposées"""
    __tablename__ = "pep_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations PEP
    person_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    country = Column(String(3), nullable=True)
    
    # Détails
    match_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    
    # Dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Références
    external_id = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    
    # Statut
    is_false_positive = Column(Boolean, default=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<PEPMatch(id={self.id}, user_id={self.user_id}, person='{self.person_name}')>"


class KYCPolicy(Base):
    """Politiques KYC configurables"""
    __tablename__ = "kyc_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Limites de montant
    max_transfer_amount = Column(Float, nullable=False, default=10000.0)
    max_daily_amount = Column(Float, nullable=False, default=50000.0)
    max_monthly_amount = Column(Float, nullable=False, default=200000.0)
    
    # Seuils de vérification
    enhanced_due_diligence_threshold = Column(Float, nullable=False, default=5000.0)
    manual_review_threshold = Column(Float, nullable=False, default=10000.0)
    
    # Vérifications requises
    required_documents = Column(JSON, nullable=True)  # Liste des types de documents requis
    required_checks = Column(JSON, nullable=True)  # Liste des vérifications requises
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<KYCPolicy(id={self.id}, name='{self.name}')>"