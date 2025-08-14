"""
Database configuration and session management
"""

from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import structlog
from contextlib import contextmanager

from app.config import get_settings

logger = structlog.get_logger()

# Get settings
settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    echo=settings.database.echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Base model with common fields
class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

async def init_db():
    """Initialize database"""
    try:
        logger.info("Initializing database...")
        
        # Import all models to ensure they are registered
        from app.auth.models import User, UserRoleAssignment, RefreshToken, LoginAttempt, PasswordReset, Session
        from app.accounts.models import Account, AccountActivity
        from app.transfers.models import Transfer, TransferEvent, TransferTemplate, TransferLimit
        from app.kyc.models import KYCDocument, KYCCheck, SanctionsMatch, PEPMatch, KYCPolicy
        from app.audit.models import AuditLog, SecurityEvent, DataAccessLog, ComplianceReport, AuditPolicy
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def check_db_connection():
    """Check database connection"""
    try:
        with get_db_context() as db:
            # Simple query to test connection
            db.execute("SELECT 1")
            logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def create_tables():
    """Create all tables (synchronous version)"""
    Base.metadata.create_all(bind=engine)