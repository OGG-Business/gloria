from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Numeric, Boolean, LargeBinary, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db import Base

class TransferStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    subject = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    iban = Column(String, index=True)
    bic = Column(String, index=True)
    display_name = Column(String)
    sensitive_metadata = Column(LargeBinary)  # AES-256-GCM ciphertext
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    debtor_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    creditor_iban = Column(String, index=True)
    creditor_bic = Column(String, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(TransferStatus), default=TransferStatus.INITIATED, index=True)
    reference = Column(String, index=True)
    pacs008_xml = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TransferEvent(Base):
    __tablename__ = "transfer_events"
    id = Column(Integer, primary_key=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    payload = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String, nullable=False)
    encrypted_blob = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    correlation_id = Column(String, index=True)
    actor_subject = Column(String, index=True)
    action = Column(String, nullable=False)
    target = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)