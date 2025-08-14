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
    try:
        from app.common.database import init_db, check_db_connection
        await init_db()
        await check_db_connection()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
    
    # Setup monitoring
    try:
        from app.common.monitoring import setup_monitoring
        setup_monitoring()
        logger.info("Monitoring setup completed")
    except Exception as e:
        logger.warning(f"Monitoring setup failed: {e}")
    
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

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Transfer Platform API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/auth",
            "accounts": "/accounts", 
            "transfers": "/transfers",
            "kyc": "/kyc",
            "notifications": "/notifications",
            "admin": "/admin"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.common.database import check_db_connection
        await check_db_connection()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from app.common.monitoring import get_metrics
        return get_metrics()
    except Exception as e:
        logger.error(f"Metrics failed: {e}")
        return {"error": "Metrics not available"}

# Include routers
try:
    from app.auth.routes import router as auth_router
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    logger.info("Auth router included")
except Exception as e:
    logger.warning(f"Auth router not available: {e}")

try:
    from app.accounts.routes import router as accounts_router
    app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
    logger.info("Accounts router included")
except Exception as e:
    logger.warning(f"Accounts router not available: {e}")

try:
    from app.transfers.routes import router as transfers_router
    app.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])
    logger.info("Transfers router included")
except Exception as e:
    logger.warning(f"Transfers router not available: {e}")

try:
    from app.kyc.routes import router as kyc_router
    app.include_router(kyc_router, prefix="/kyc", tags=["KYC"])
    logger.info("KYC router included")
except Exception as e:
    logger.warning(f"KYC router not available: {e}")

try:
    from app.notifications.routes import router as notifications_router
    app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
    logger.info("Notifications router included")
except Exception as e:
    logger.warning(f"Notifications router not available: {e}")

try:
    from app.admin.routes import router as admin_router
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    logger.info("Admin router included")
except Exception as e:
    logger.warning(f"Admin router not available: {e}")

# Global exception handler
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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )