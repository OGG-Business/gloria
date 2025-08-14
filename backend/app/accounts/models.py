"""
Account models for Banking Transfer Platform
"""

import uuid
from datetime import datetime
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.common.database import BaseModel

class AccountStatus(str, Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    PENDING_VERIFICATION = "pending_verification"

class AccountType(str, Enum):
    """Account type enumeration"""
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"
    ESCROW = "escrow"

class Currency(str, Enum):
    """Currency enumeration"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CDF = "CDF"  # Congolese Franc
    XAF = "XAF"  # Central African CFA
    XOF = "XOF"  # West African CFA

class Account(BaseModel):
    """Account model"""
    __tablename__ = "accounts"
    
    # Basic information
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    account_number = Column(String(50), unique=True, index=True, nullable=False)
    iban = Column(String(34), unique=True, index=True, nullable=True)
    bic = Column(String(11), nullable=True)
    
    # Account details
    name = Column(String(100), nullable=False)
    type = Column(SQLEnum(AccountType), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False)
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.PENDING_VERIFICATION, nullable=False)
    
    # Balance and limits
    balance = Column(Numeric(20, 2), default=0, nullable=False)
    available_balance = Column(Numeric(20, 2), default=0, nullable=False)
    daily_limit = Column(Numeric(20, 2), nullable=True)
    monthly_limit = Column(Numeric(20, 2), nullable=True)
    
    # Bank information
    bank_name = Column(String(100), nullable=True)
    bank_code = Column(String(20), nullable=True)
    branch_code = Column(String(20), nullable=True)
    country_code = Column(String(2), nullable=False)
    
    # Security
    is_default = Column(Boolean, default=False, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", backref="accounts")
    activities = relationship("AccountActivity", back_populates="account")
    incoming_transfers = relationship("Transfer", foreign_keys="Transfer.recipient_account_id", back_populates="recipient_account")
    outgoing_transfers = relationship("Transfer", foreign_keys="Transfer.sender_account_id", back_populates="sender_account")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.account_number:
            self.account_number = self._generate_account_number()
    
    def _generate_account_number(self) -> str:
        """Generate unique account number"""
        return f"ACC{uuid.uuid4().hex[:12].upper()}"
    
    def can_debit(self, amount: Decimal) -> bool:
        """Check if account can be debited"""
        if self.status != AccountStatus.ACTIVE:
            return False
        if self.available_balance < amount:
            return False
        return True
    
    def debit(self, amount: Decimal):
        """Debit account"""
        if not self.can_debit(amount):
            raise ValueError("Insufficient funds or account not active")
        self.balance -= amount
        self.available_balance -= amount
    
    def credit(self, amount: Decimal):
        """Credit account"""
        if self.status != AccountStatus.ACTIVE:
            raise ValueError("Account not active")
        self.balance += amount
        self.available_balance += amount
    
    def get_formatted_balance(self) -> str:
        """Get formatted balance string"""
        return f"{self.balance:.2f} {self.currency}"

class AccountActivity(BaseModel):
    """Account activity model"""
    __tablename__ = "account_activities"
    
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    transfer_id = Column(String(36), ForeignKey("transfers.id"), nullable=True)
    
    # Activity details
    type = Column(String(50), nullable=False)  # debit, credit, fee, adjustment
    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False)
    balance_before = Column(Numeric(20, 2), nullable=False)
    balance_after = Column(Numeric(20, 2), nullable=False)
    
    # Description
    description = Column(Text, nullable=False)
    reference = Column(String(100), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    account = relationship("Account", back_populates="activities")
    transfer = relationship("Transfer", backref="account_activities")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def get_formatted_amount(self) -> str:
        """Get formatted amount string"""
        return f"{self.amount:.2f} {self.currency}"