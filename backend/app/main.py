from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from .services.logging import configure_logging, with_request_id
from .routers import accounts, transfers, kyc, admin, hooks, auth_router, notifications
from .config import settings
from .db import get_engine

configure_logging()

app = FastAPI(title="OpenBank Transfers Platform", version="1.0.0")

# CORS for web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    if settings.use_db:
        get_engine()


@app.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    response = await with_request_id(request, call_next)
    return response


@app.get("/health", tags=["ops"])  # simple health check
def health() -> dict:
    return {"status": "ok", "db": bool(settings.use_db)}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
app.include_router(kyc.router, prefix="/kyc", tags=["kyc"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(hooks.router, prefix="/hooks", tags=["hooks"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])