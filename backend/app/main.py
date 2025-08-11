"""
Application principale FastAPI pour Banking Transfer Platform
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import structlog

from app.config import get_settings
from app.common.database import init_db, check_db_connection
from app.auth.routes import auth_router
from app.accounts.routes import accounts_router
from app.transfers.routes import transfers_router
from app.kyc.routes import kyc_router
from app.notifications.routes import notifications_router
from app.admin.routes import admin_router
from app.common.middleware import AuditMiddleware, SecurityMiddleware
from app.common.monitoring import setup_monitoring

# Configuration du logging structuré
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

# Configuration
settings = get_settings()

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("Starting Banking Transfer Platform", version=settings.version)
    
    # Vérifier la connexion à la base de données
    if not check_db_connection():
        logger.error("Database connection failed")
        raise RuntimeError("Database connection failed")
    
    # Initialiser la base de données
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    # Setup monitoring
    setup_monitoring()
    logger.info("Monitoring setup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Banking Transfer Platform")


# Création de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Plateforme complète de transferts bancaires avec support SWIFT et Mojaloop",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else settings.cors_origins
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware personnalisés
app.add_middleware(AuditMiddleware)
app.add_middleware(SecurityMiddleware)


# Routes de base
@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Banking Transfer Platform API",
        "version": settings.version,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'application"""
    health_status = {
        "status": "healthy",
        "version": settings.version,
        "environment": settings.environment,
        "checks": {}
    }
    
    # Vérifier la base de données
    try:
        db_healthy = check_db_connection()
        health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
        if not db_healthy:
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Vérifier Redis
    try:
        # TODO: Implémenter vérification Redis
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Vérifier les connecteurs bancaires
    try:
        # TODO: Implémenter vérification connecteurs
        health_status["checks"]["swift_connector"] = "healthy"
        health_status["checks"]["mojaloop_connector"] = "healthy"
    except Exception as e:
        health_status["checks"]["connectors"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


@app.get("/metrics")
async def metrics():
    """Endpoint Prometheus pour les métriques"""
    # TODO: Implémenter métriques Prometheus
    return {"message": "Metrics endpoint - to be implemented"}


# Inclusion des routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
app.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])
app.include_router(kyc_router, prefix="/kyc", tags=["KYC"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/admin", tags=["Administration"])


# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }


# Gestionnaire d'erreurs 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Gestionnaire d'erreurs 404"""
    return {
        "error": "Not found",
        "message": f"The requested resource {request.url.path} was not found",
        "status_code": 404
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
        log_level=settings.monitoring.log_level.lower()
    )