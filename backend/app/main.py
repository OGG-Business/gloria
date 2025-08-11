import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .core.config import settings
from .routers import accounts, transfers, kyc, admin, hooks, auth

app = FastAPI(title=settings.app_name, version="0.1.0")

# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
app.include_router(kyc.router, prefix="/kyc", tags=["kyc"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(hooks.router, prefix="/hooks", tags=["hooks"])


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}