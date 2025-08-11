"""
Database configuration and connection management
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import asyncio

from app.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Get database session context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they are registered
        from app.accounts.models import Account, AccountActivity
        from app.transfers.models import Transfer, TransferEvent, TransferTemplate, TransferLimit
        from app.auth.models import User, UserRole, RefreshToken, LoginAttempt, PasswordReset, Session
        from app.kyc.models import KYCDocument, KYCCheck, SanctionsMatch, PEPMatch, KYCPolicy
        from app.audit.models import AuditLog, SecurityEvent, DataAccessLog, ComplianceReport, AuditPolicy
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def check_db_connection():
    """Check database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def create_tables():
    """Create database tables (synchronous version)"""
    try:
        # Import all models
        from app.accounts.models import Account, AccountActivity
        from app.transfers.models import Transfer, TransferEvent, TransferTemplate, TransferLimit
        from app.auth.models import User, UserRole, RefreshToken, LoginAttempt, PasswordReset, Session
        from app.kyc.models import KYCDocument, KYCCheck, SanctionsMatch, PEPMatch, KYCPolicy
        from app.audit.models import AuditLog, SecurityEvent, DataAccessLog, ComplianceReport, AuditPolicy
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise