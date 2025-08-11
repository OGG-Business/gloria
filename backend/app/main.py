"""
Main FastAPI application entry point
"""

import logging
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.common.database import init_db, check_db_connection
from app.common.monitoring import setup_monitoring
from app.auth.routes import router as auth_router
from app.accounts.routes import router as accounts_router
from app.transfers.routes import router as transfers_router
from app.kyc.routes import router as kyc_router
from app.notifications.routes import router as notifications_router
from app.admin.routes import router as admin_router

# Configure structured logging
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
    logger.info("Starting Banking Transfer Platform...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Setup monitoring
        setup_monitoring()
        logger.info("Monitoring setup completed")
        
        # Check database connection
        await check_db_connection()
        logger.info("Database connection verified")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Banking Transfer Platform...")

# Create FastAPI app
app = FastAPI(
    title="Banking Transfer Platform",
    description="Secure banking transfers with SWIFT and IBAN support",
    version="1.0.0",
    docs_url="/docs" if True else None,  # Enable docs in development
    redoc_url="/redoc" if True else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
from app.common.middleware import AuditMiddleware, SecurityMiddleware
app.add_middleware(AuditMiddleware)
app.add_middleware(SecurityMiddleware)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Transfer Platform API",
        "version": "1.0.0",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await check_db_connection()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2023-12-01T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from app.common.monitoring import metrics_endpoint
    return metrics_endpoint()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
app.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])
app.include_router(kyc_router, prefix="/kyc", tags=["KYC"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )