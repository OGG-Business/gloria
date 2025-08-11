"""
Main FastAPI application for Banking Transfer Platform
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from app.config import get_settings
from app.common.database import init_db, check_db_connection
from app.common.middleware import AuditMiddleware, SecurityMiddleware
from app.common.monitoring import setup_monitoring

# Import routers
from app.auth.routes import router as auth_router
from app.accounts.routes import router as accounts_router
from app.transfers.routes import router as transfers_router
from app.kyc.routes import router as kyc_router
from app.notifications.routes import router as notifications_router
from app.admin.routes import router as admin_router

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Banking Transfer Platform")
    
    # Initialize database
    await init_db()
    await check_db_connection()
    
    # Setup monitoring
    setup_monitoring()
    
    logger.info("Banking Transfer Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Banking Transfer Platform")

# Create FastAPI app
app = FastAPI(
    title="Banking Transfer Platform",
    description="A complete cloud-native platform for real bank transfers (SWIFT & IBAN)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(AuditMiddleware)
app.add_middleware(SecurityMiddleware)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
app.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])
app.include_router(kyc_router, prefix="/kyc", tags=["KYC"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Transfer Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await check_db_connection()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from app.common.monitoring import get_metrics
    return get_metrics()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers
    )