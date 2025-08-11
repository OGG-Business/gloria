"""
Account models for Banking Transfer Platform
"""

from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base

class AccountType(enum.Enum):
    """Account types"""
    CURRENT = "current"
    SAVINGS = "savings"
    BUSINESS = "business"

class AccountStatus(enum.Enum):
    """Account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    PENDING = "pending"

class Currency(enum.Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    CDF = "CDF"
    GBP = "GBP"
    CHF = "CHF"

class Account(Base):
    """Account model"""
    __tablename__ = "accounts"
    
    id = Column(String(36), primary_key=True)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    iban = Column(String(34), unique=True, nullable=True, index=True)
    bic = Column(String(11), nullable=True)
    holder_name = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    available_balance = Column(Float, default=0.0, nullable=False)
    blocked_amount = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    currency = Column(Enum(Currency), default=Currency.USD, nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.CURRENT, nullable=False)
    daily_limit = Column(Float, default=10000.0, nullable=False)
    monthly_limit = Column(Float, default=100000.0, nullable=False)
    daily_used = Column(Float, default=0.0, nullable=False)
    monthly_used = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="accounts")
    
    # Transfer relationships
    outgoing_transfers = relationship("Transfer", foreign_keys="Transfer.source_account_id", back_populates="source_account")
    incoming_transfers = relationship("Transfer", foreign_keys="Transfer.destination_account_id", back_populates="destination_account")
    
    # Activity relationship
    activities = relationship("AccountActivity", back_populates="account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, account_number={self.account_number}, balance={self.balance})>"
    
    def block_amount(self, amount: float) -> bool:
        """Block amount from available balance"""
        if self.available_balance >= amount:
            self.available_balance -= amount
            self.blocked_amount += amount
            return True
        return False
    
    def unblock_amount(self, amount: float) -> bool:
        """Unblock amount back to available balance"""
        if self.blocked_amount >= amount:
            self.blocked_amount -= amount
            self.available_balance += amount
            return True
        return False
    
    def debit(self, amount: float) -> bool:
        """Debit amount from account"""
        if self.available_balance >= amount:
            self.available_balance -= amount
            self.balance -= amount
            return True
        return False
    
    def credit(self, amount: float) -> bool:
        """Credit amount to account"""
        self.available_balance += amount
        self.balance += amount
        return True
    
    @property
    def is_active(self) -> bool:
        """Check if account is active"""
        return self.status == AccountStatus.ACTIVE
    
    @property
    def can_transfer(self) -> bool:
        """Check if account can perform transfers"""
        return self.is_active and self.available_balance > 0

class AccountActivity(Base):
    """Account activity model for transaction history"""
    __tablename__ = "account_activities"
    
    id = Column(String(36), primary_key=True)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # credit, debit, transfer_in, transfer_out
    amount = Column(Float, nullable=False)
    currency = Column(Enum(Currency), nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)  # Transfer ID, etc.
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="activities")
    
    def __repr__(self):
        return f"<AccountActivity(id={self.id}, type={self.activity_type}, amount={self.amount})>"