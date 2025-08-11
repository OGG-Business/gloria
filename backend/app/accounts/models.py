"""
Modèles de base de données pour les comptes bancaires
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.common.database import Base


class AccountType(str, enum.Enum):
    """Types de comptes bancaires"""
    CURRENT = "current"
    SAVINGS = "savings"
    BUSINESS = "business"
    FOREIGN = "foreign"


class AccountStatus(str, enum.Enum):
    """Statuts des comptes"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    PENDING_VERIFICATION = "pending_verification"


class Currency(str, enum.Enum):
    """Devises supportées"""
    USD = "USD"
    EUR = "EUR"
    CDF = "CDF"  # Franc congolais
    XAF = "XAF"  # Franc CFA
    GBP = "GBP"
    CHF = "CHF"


class Account(Base):
    """Modèle de compte bancaire"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, index=True, nullable=False)
    iban = Column(String(34), unique=True, index=True, nullable=True)
    bic = Column(String(11), nullable=True)
    
    # Informations du titulaire
    holder_name = Column(String(255), nullable=False)
    holder_id = Column(String(50), nullable=False)  # ID national/passport
    holder_email = Column(String(255), nullable=False)
    holder_phone = Column(String(20), nullable=True)
    
    # Informations bancaires
    bank_name = Column(String(255), nullable=False)
    bank_code = Column(String(20), nullable=False)
    branch_code = Column(String(20), nullable=True)
    
    # Type et statut
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.CURRENT)
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    currency = Column(Enum(Currency), nullable=False, default=Currency.USD)
    
    # Soldes
    balance = Column(Float, nullable=False, default=0.0)
    available_balance = Column(Float, nullable=False, default=0.0)
    blocked_amount = Column(Float, nullable=False, default=0.0)
    
    # Limites
    daily_limit = Column(Float, nullable=False, default=10000.0)
    monthly_limit = Column(Float, nullable=False, default=100000.0)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="accounts")
    
    # Transferts sortants
    outgoing_transfers = relationship("Transfer", foreign_keys="Transfer.source_account_id", back_populates="source_account")
    
    # Transferts entrants
    incoming_transfers = relationship("Transfer", foreign_keys="Transfer.destination_account_id", back_populates="destination_account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, account_number='{self.account_number}', holder='{self.holder_name}')>"
    
    @property
    def is_active(self) -> bool:
        """Vérifie si le compte est actif"""
        return self.status == AccountStatus.ACTIVE
    
    @property
    def can_transfer(self) -> bool:
        """Vérifie si le compte peut effectuer des transferts"""
        return self.is_active and self.available_balance > 0
    
    def has_sufficient_funds(self, amount: float) -> bool:
        """Vérifie si le compte a suffisamment de fonds"""
        return self.available_balance >= amount
    
    def block_amount(self, amount: float) -> bool:
        """Bloque un montant sur le compte"""
        if self.has_sufficient_funds(amount):
            self.available_balance -= amount
            self.blocked_amount += amount
            return True
        return False
    
    def unblock_amount(self, amount: float) -> bool:
        """Débloque un montant sur le compte"""
        if self.blocked_amount >= amount:
            self.blocked_amount -= amount
            self.available_balance += amount
            return True
        return False
    
    def debit(self, amount: float) -> bool:
        """Débite le compte"""
        if self.has_sufficient_funds(amount):
            self.balance -= amount
            self.available_balance -= amount
            self.last_activity = datetime.utcnow()
            return True
        return False
    
    def credit(self, amount: float) -> bool:
        """Crédite le compte"""
        self.balance += amount
        self.available_balance += amount
        self.last_activity = datetime.utcnow()
        return True


class AccountActivity(Base):
    """Historique des activités du compte"""
    __tablename__ = "account_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    # Type d'activité
    activity_type = Column(String(50), nullable=False)  # transfer, deposit, withdrawal, etc.
    description = Column(Text, nullable=False)
    
    # Montants
    amount = Column(Float, nullable=False)
    currency = Column(Enum(Currency), nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    
    # Références
    reference_id = Column(String(100), nullable=True)  # ID du transfert, etc.
    reference_type = Column(String(50), nullable=True)  # transfer, etc.
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relations
    account = relationship("Account", back_populates="activities")
    
    def __repr__(self):
        return f"<AccountActivity(id={self.id}, account_id={self.account_id}, type='{self.activity_type}')>"


# Ajouter la relation dans le modèle Account
Account.activities = relationship("AccountActivity", back_populates="account", order_by="AccountActivity.created_at.desc()")