"""
Transfer models for Banking Transfer Platform
"""

import uuid
from datetime import datetime
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.common.database import BaseModel

class TransferStatus(str, Enum):
    """Transfer status enumeration"""
    INITIATED = "initiated"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TransferType(str, Enum):
    """Transfer type enumeration"""
    SWIFT = "swift"
    SEPA = "sepa"
    MOJALOOP = "mojaloop"
    LOCAL = "local"
    INTERNAL = "internal"

class TransferPriority(str, Enum):
    """Transfer priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Transfer(BaseModel):
    """Transfer model"""
    __tablename__ = "transfers"
    
    # Basic information
    transfer_id = Column(String(50), unique=True, index=True, nullable=False)
    sender_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sender_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    recipient_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    
    # Transfer details
    type = Column(SQLEnum(TransferType), nullable=False)
    status = Column(SQLEnum(TransferStatus), default=TransferStatus.INITIATED, nullable=False)
    priority = Column(SQLEnum(TransferPriority), default=TransferPriority.NORMAL, nullable=False)
    
    # Amount and currency
    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    exchange_rate = Column(Numeric(10, 6), nullable=True)
    converted_amount = Column(Numeric(20, 2), nullable=True)
    converted_currency = Column(String(3), nullable=True)
    
    # Fees
    fee_amount = Column(Numeric(20, 2), default=0, nullable=False)
    fee_currency = Column(String(3), nullable=False)
    total_amount = Column(Numeric(20, 2), nullable=False)  # amount + fees
    
    # Recipient information
    recipient_name = Column(String(255), nullable=False)
    recipient_iban = Column(String(34), nullable=True)
    recipient_bic = Column(String(11), nullable=True)
    recipient_bank_name = Column(String(100), nullable=True)
    recipient_bank_code = Column(String(20), nullable=True)
    recipient_country = Column(String(2), nullable=False)
    
    # Transfer details
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    purpose_code = Column(String(4), nullable=True)
    
    # Processing
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # External references
    external_reference = Column(String(100), nullable=True)
    swift_message_id = Column(String(50), nullable=True)
    iso20022_message_id = Column(String(50), nullable=True)
    
    # Compliance
    requires_approval = Column(Boolean, default=False, nullable=False)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    compliance_checked = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    sender_user = relationship("User", foreign_keys=[sender_user_id])
    sender_account = relationship("Account", foreign_keys=[sender_account_id], back_populates="outgoing_transfers")
    recipient_account = relationship("Account", foreign_keys=[recipient_account_id], back_populates="incoming_transfers")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    events = relationship("TransferEvent", back_populates="transfer")
    template = relationship("TransferTemplate", back_populates="transfers")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.transfer_id:
            self.transfer_id = self._generate_transfer_id()
        if not self.total_amount:
            self.total_amount = self.amount + self.fee_amount
    
    def _generate_transfer_id(self) -> str:
        """Generate unique transfer ID"""
        return f"TXN{uuid.uuid4().hex[:12].upper()}"
    
    def can_be_processed(self) -> bool:
        """Check if transfer can be processed"""
        if self.status not in [TransferStatus.INITIATED, TransferStatus.PENDING]:
            return False
        if self.requires_approval and not self.approved_by:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def get_formatted_amount(self) -> str:
        """Get formatted amount string"""
        return f"{self.amount:.2f} {self.currency}"
    
    def get_total_formatted_amount(self) -> str:
        """Get formatted total amount string"""
        return f"{self.total_amount:.2f} {self.currency}"

class TransferEvent(BaseModel):
    """Transfer event model"""
    __tablename__ = "transfer_events"
    
    transfer_id = Column(String(36), ForeignKey("transfers.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # status_change, fee_calculated, etc.
    status_from = Column(SQLEnum(TransferStatus), nullable=True)
    status_to = Column(SQLEnum(TransferStatus), nullable=True)
    
    # Event data
    description = Column(Text, nullable=False)
    data = Column(JSONB, nullable=True)
    
    # Processing
    processed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    external_reference = Column(String(100), nullable=True)
    
    # Relationships
    transfer = relationship("Transfer", back_populates="events")
    processed_by_user = relationship("User", foreign_keys=[processed_by])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())

class TransferTemplate(BaseModel):
    """Transfer template model"""
    __tablename__ = "transfer_templates"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Template details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Transfer details
    type = Column(SQLEnum(TransferType), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    recipient_iban = Column(String(34), nullable=True)
    recipient_bic = Column(String(11), nullable=True)
    recipient_bank_name = Column(String(100), nullable=True)
    recipient_country = Column(String(2), nullable=False)
    
    # Default values
    default_amount = Column(Numeric(20, 2), nullable=True)
    default_currency = Column(String(3), nullable=False)
    default_description = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", backref="transfer_templates")
    transfers = relationship("Transfer", back_populates="template")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())

class TransferLimit(BaseModel):
    """Transfer limit model"""
    __tablename__ = "transfer_limits"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Limit details
    limit_type = Column(String(50), nullable=False)  # daily, monthly, per_transfer
    currency = Column(String(3), nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)
    
    # Usage tracking
    used_amount = Column(Numeric(20, 2), default=0, nullable=False)
    reset_date = Column(DateTime(timezone=True), nullable=False)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", backref="transfer_limits")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def can_transfer(self, amount: Decimal) -> bool:
        """Check if transfer is within limit"""
        if not self.is_active:
            return False
        if self.used_amount + amount > self.amount:
            return False
        return True
    
    def record_transfer(self, amount: Decimal):
        """Record transfer against limit"""
        self.used_amount += amount
    
    def get_remaining_amount(self) -> Decimal:
        """Get remaining amount in limit"""
        return max(0, self.amount - self.used_amount)