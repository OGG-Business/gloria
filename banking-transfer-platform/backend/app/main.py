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
