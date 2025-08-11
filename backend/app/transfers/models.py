"""
Modèles de base de données pour les transferts bancaires
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.common.database import Base


class TransferType(str, enum.Enum):
    """Types de transferts"""
    SWIFT = "swift"
    SEPA = "sepa"
    MOJALOOP = "mojaloop"
    LOCAL = "local"


class TransferStatus(str, enum.Enum):
    """Statuts des transferts"""
    INITIATED = "initiated"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TransferPriority(str, enum.Enum):
    """Priorités des transferts"""
    NORMAL = "normal"
    URGENT = "urgent"
    HIGH = "high"


class Transfer(Base):
    """Modèle de transfert bancaire"""
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(String(50), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Type et statut
    transfer_type = Column(Enum(TransferType), nullable=False)
    status = Column(Enum(TransferStatus), nullable=False, default=TransferStatus.INITIATED)
    priority = Column(Enum(TransferPriority), nullable=False, default=TransferPriority.NORMAL)
    
    # Comptes source et destination
    source_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    destination_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    # Montants
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    exchange_rate = Column(Float, nullable=True)
    converted_amount = Column(Float, nullable=True)
    
    # Frais
    fees = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)  # amount + fees
    
    # Informations de destination
    beneficiary_name = Column(String(255), nullable=False)
    beneficiary_bank = Column(String(255), nullable=False)
    beneficiary_iban = Column(String(34), nullable=True)
    beneficiary_bic = Column(String(11), nullable=True)
    beneficiary_account = Column(String(50), nullable=True)
    
    # Références bancaires
    swift_message_id = Column(String(50), nullable=True)
    mojaloop_transfer_id = Column(String(50), nullable=True)
    external_reference = Column(String(100), nullable=True)
    
    # Instructions
    purpose = Column(String(255), nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    source_account = relationship("Account", foreign_keys=[source_account_id], back_populates="outgoing_transfers")
    destination_account = relationship("Account", foreign_keys=[destination_account_id], back_populates="incoming_transfers")
    events = relationship("TransferEvent", back_populates="transfer", order_by="TransferEvent.created_at")
    
    # Données techniques
    technical_data = Column(JSON, nullable=True)  # Données SWIFT, Mojaloop, etc.
    
    def __repr__(self):
        return f"<Transfer(id={self.id}, transfer_id='{self.transfer_id}', status='{self.status}')>"
    
    @property
    def is_completed(self) -> bool:
        """Vérifie si le transfert est terminé"""
        return self.status == TransferStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Vérifie si le transfert a échoué"""
        return self.status in [TransferStatus.FAILED, TransferStatus.REJECTED, TransferStatus.CANCELLED]
    
    @property
    def is_pending(self) -> bool:
        """Vérifie si le transfert est en attente"""
        return self.status in [TransferStatus.INITIATED, TransferStatus.PENDING, TransferStatus.PROCESSING]
    
    def can_cancel(self) -> bool:
        """Vérifie si le transfert peut être annulé"""
        return self.status in [TransferStatus.INITIATED, TransferStatus.PENDING]
    
    def get_latest_event(self):
        """Retourne le dernier événement du transfert"""
        return self.events[-1] if self.events else None


class TransferEvent(Base):
    """Événements de suivi des transferts"""
    __tablename__ = "transfer_events"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    
    # Type d'événement
    event_type = Column(String(50), nullable=False)  # initiated, sent_to_swift, completed, etc.
    event_code = Column(String(20), nullable=True)  # Code SWIFT, etc.
    
    # Description
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Détails techniques
    
    # Statut
    status = Column(Enum(TransferStatus), nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_by = Column(String(100), nullable=True)  # Système ou utilisateur
    
    # Relations
    transfer = relationship("Transfer", back_populates="events")
    
    def __repr__(self):
        return f"<TransferEvent(id={self.id}, transfer_id={self.transfer_id}, type='{self.event_type}')>"


class TransferTemplate(Base):
    """Templates de transferts pour les transferts récurrents"""
    __tablename__ = "transfer_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration du transfert
    source_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    beneficiary_name = Column(String(255), nullable=False)
    beneficiary_bank = Column(String(255), nullable=False)
    beneficiary_iban = Column(String(34), nullable=True)
    beneficiary_bic = Column(String(11), nullable=True)
    beneficiary_account = Column(String(50), nullable=True)
    
    # Montant par défaut
    default_amount = Column(Float, nullable=True)
    currency = Column(String(3), nullable=False)
    
    # Instructions par défaut
    default_purpose = Column(String(255), nullable=True)
    default_instructions = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relations
    source_account = relationship("Account")
    
    def __repr__(self):
        return f"<TransferTemplate(id={self.id}, name='{self.name}')>"


class TransferLimit(Base):
    """Limites de transfert par utilisateur/compte"""
    __tablename__ = "transfer_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Null pour limites globales
    
    # Limites
    daily_limit = Column(Float, nullable=False)
    monthly_limit = Column(Float, nullable=False)
    yearly_limit = Column(Float, nullable=False)
    
    # Compteurs
    daily_used = Column(Float, nullable=False, default=0.0)
    monthly_used = Column(Float, nullable=False, default=0.0)
    yearly_used = Column(Float, nullable=False, default=0.0)
    
    # Devise
    currency = Column(String(3), nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User")
    account = relationship("Account")
    
    def __repr__(self):
        return f"<TransferLimit(id={self.id}, user_id={self.user_id}, daily_limit={self.daily_limit})>"
    
    def can_transfer(self, amount: float) -> bool:
        """Vérifie si un transfert peut être effectué"""
        return (
            self.daily_used + amount <= self.daily_limit and
            self.monthly_used + amount <= self.monthly_limit and
            self.yearly_used + amount <= self.yearly_limit
        )
    
    def record_transfer(self, amount: float) -> None:
        """Enregistre un transfert dans les compteurs"""
        self.daily_used += amount
        self.monthly_used += amount
        self.yearly_used += amount