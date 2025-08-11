import ssl
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import Settings, get_settings
from app.observability.metrics import configure_logging, CorrelationIdMiddleware
from app.auth.routes import router as auth_router
from app.accounts.routes import router as accounts_router
from app.transfers.routes import router as transfers_router
from app.kyc.routes import router as kyc_router
from app.notifications.routes import router as notifications_router
from app.hooks.routes import router as hooks_router
from app.admin.routes import router as admin_router

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
import os

settings: Settings = get_settings()
configure_logging()

app = FastAPI(title="Global Payments Platform", version="0.1.0")

@app.on_event("startup")
async def run_migrations():
    alembic_cfg = AlembicConfig(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    alembic_command.upgrade(alembic_cfg, "head")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(transfers_router, prefix="/transfers", tags=["transfers"])
app.include_router(kyc_router, prefix="/kyc", tags=["kyc"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(hooks_router, prefix="/hooks", tags=["hooks"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

@app.get("/healthz")
async def health() -> dict:
    return {"status": "ok"}

Instrumentator().instrument(app).expose(app, include_in_schema=False)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8443,
        reload=False,
        ssl_keyfile=settings.tls_key_path,
        ssl_certfile=settings.tls_cert_path,
        ssl_version=ssl.PROTOCOL_TLSv1_3 if hasattr(__import__('ssl'), 'PROTOCOL_TLSv1_3') else None,
    )