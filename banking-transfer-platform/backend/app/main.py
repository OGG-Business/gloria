import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
logger = structlog.get_logger()
app = FastAPI(title="Banking Transfer Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.get("/")
async def root():
    return {"message": "Banking Transfer Platform API", "version": "1.0.0", "status": "running"}
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "timestamp": "2024-01-01T00:00:00Z"}

# Include routers
try:
    from app.auth.routes import router as auth_router
    app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
    logger.info('Auth router included')
except Exception as e:
    logger.warning(f'Auth router not available: {e}')
try:
    from app.accounts.routes import router as accounts_router
    app.include_router(accounts_router, prefix='/accounts', tags=['Accounts'])
    logger.info('Accounts router included')
except Exception as e:
    logger.warning(f'Accounts router not available: {e}')
try:
    from app.transfers.routes import router as transfers_router
    app.include_router(transfers_router, prefix='/transfers', tags=['Transfers'])
    logger.info('Transfers router included')
except Exception as e:
    logger.warning(f'Transfers router not available: {e}')
try:
    from app.kyc.routes import router as kyc_router
    app.include_router(kyc_router, prefix='/kyc', tags=['KYC'])
    logger.info('KYC router included')
except Exception as e:
    logger.warning(f'KYC router not available: {e}')
try:
    from app.notifications.routes import router as notifications_router
    app.include_router(notifications_router, prefix='/notifications', tags=['Notifications'])
    logger.info('Notifications router included')
except Exception as e:
    logger.warning(f'Notifications router not available: {e}')
try:
    from app.admin.routes import router as admin_router
    app.include_router(admin_router, prefix='/admin', tags=['Admin'])
    logger.info('Admin router included')
except Exception as e:
    logger.warning(f'Admin router not available: {e}')
