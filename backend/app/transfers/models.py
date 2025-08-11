"""
Transfer models for Banking Transfer Platform
"""

from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base

class TransferType(enum.Enum):
    """Transfer types"""
    SWIFT = "swift"
    IBAN = "iban"
    MOJALOOP = "mojaloop"
    INTERNAL = "internal"

class TransferStatus(enum.Enum):
    """Transfer status"""
    INITIATED = "initiated"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TransferPriority(enum.Enum):
    """Transfer priority"""
    NORMAL = "normal"
    URGENT = "urgent"
    EXPRESS = "express"

class Transfer(Base):
    """Transfer model"""
    __tablename__ = "transfers"
    
    id = Column(String(36), primary_key=True)
    transfer_id = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    fees = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)  # amount + fees
    
    # Source account
    source_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    
    # Destination details
    destination_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    beneficiary_name = Column(String(255), nullable=False)
    beneficiary_iban = Column(String(34), nullable=True)
    beneficiary_bic = Column(String(11), nullable=True)
    beneficiary_bank = Column(String(255), nullable=True)
    beneficiary_country = Column(String(2), nullable=True)
    
    # Transfer details
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    transfer_type = Column(Enum(TransferType), nullable=False)
    status = Column(Enum(TransferStatus), default=TransferStatus.INITIATED, nullable=False)
    priority = Column(Enum(TransferPriority), default=TransferPriority.NORMAL, nullable=False)
    
    # External references
    swift_message_id = Column(String(100), nullable=True)
    mojaloop_transfer_id = Column(String(100), nullable=True)
    iso20022_message_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    source_account = relationship("Account", foreign_keys=[source_account_id], back_populates="outgoing_transfers")
    destination_account = relationship("Account", foreign_keys=[destination_account_id], back_populates="incoming_transfers")
    events = relationship("TransferEvent", back_populates="transfer", order_by="TransferEvent.created_at")
    
    def __repr__(self):
        return f"<Transfer(id={self.id}, transfer_id={self.transfer_id}, amount={self.amount}, status={self.status})>"
    
    @property
    def is_completed(self) -> bool:
        """Check if transfer is completed"""
        return self.status == TransferStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if transfer failed"""
        return self.status in [TransferStatus.FAILED, TransferStatus.REJECTED]
    
    @property
    def is_pending(self) -> bool:
        """Check if transfer is pending"""
        return self.status in [TransferStatus.INITIATED, TransferStatus.PENDING, TransferStatus.PROCESSING]
    
    @property
    def can_cancel(self) -> bool:
        """Check if transfer can be cancelled"""
        return self.status in [TransferStatus.INITIATED, TransferStatus.PENDING]

class TransferEvent(Base):
    """Transfer event model for tracking transfer lifecycle"""
    __tablename__ = "transfer_events"
    
    id = Column(String(36), primary_key=True)
    transfer_id = Column(String(36), ForeignKey("transfers.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # initiated, processing, completed, failed, etc.
    status = Column(Enum(TransferStatus), nullable=False)
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    transfer = relationship("Transfer", back_populates="events")
    
    def __repr__(self):
        return f"<TransferEvent(id={self.id}, transfer_id={self.transfer_id}, event_type={self.event_type})>"

class TransferTemplate(Base):
    """Transfer template for recurring transfers"""
    __tablename__ = "transfer_templates"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template details
    source_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    beneficiary_name = Column(String(255), nullable=False)
    beneficiary_iban = Column(String(34), nullable=True)
    beneficiary_bic = Column(String(11), nullable=True)
    beneficiary_bank = Column(String(255), nullable=True)
    beneficiary_country = Column(String(2), nullable=True)
    
    # Amount and frequency
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    next_execution = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<TransferTemplate(id={self.id}, name={self.name}, amount={self.amount})>"

class TransferLimit(Base):
    """Transfer limits for users and accounts"""
    __tablename__ = "transfer_limits"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    
    # Limit types
    limit_type = Column(String(50), nullable=False)  # daily, monthly, per_transaction
    currency = Column(String(3), nullable=False)
    max_amount = Column(Float, nullable=False)
    current_used = Column(Float, default=0.0, nullable=False)
    
    # Reset period
    reset_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<TransferLimit(id={self.id}, limit_type={self.limit_type}, max_amount={self.max_amount})>"
    
    @property
    def remaining_amount(self) -> float:
        """Get remaining amount for this limit"""
        return max(0, self.max_amount - self.current_used)
    
    @property
    def is_exceeded(self) -> bool:
        """Check if limit is exceeded"""
        return self.current_used >= self.max_amount