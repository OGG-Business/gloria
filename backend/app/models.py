from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .db import Base


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    iban = Column(String, index=True, nullable=False)
    bic = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True, index=True)
    debtor_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    creditor_name = Column(String, nullable=False)
    creditor_iban = Column(String, nullable=False)
    creditor_bic = Column(String, nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(String, default="INITIATED", index=True, nullable=False)
    metadata = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    debtor_account = relationship("Account")
    events = relationship("TransferEvent", back_populates="transfer")


class TransferEvent(Base):
    __tablename__ = "transfer_events"
    id = Column(Integer, primary_key=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), index=True, nullable=False)
    type = Column(String, nullable=False)  # INITIATED, PENDING, COMPLETED, FAILED
    payload = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transfer = relationship("Transfer", back_populates="events")


class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    doc_type = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    encrypted_blob = Column(Text, nullable=False)  # base64(nonce:ciphertext:tag)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    trace_id = Column(String, index=True, nullable=False)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    details = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)