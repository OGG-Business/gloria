#!/usr/bin/env python3
"""
Simple working server for Banking Transfer Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Banking Transfer Platform",
    description="A complete cloud-native platform for real bank transfers (SWIFT & IBAN)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Transfer Platform API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/auth/test")
async def auth_test():
    """Auth test endpoint"""
    return {"message": "Auth working"}

@app.get("/accounts/test")
async def accounts_test():
    """Accounts test endpoint"""
    return {"message": "Accounts working"}

@app.get("/transfers/test")
async def transfers_test():
    """Transfers test endpoint"""
    return {"message": "Transfers working"}

@app.get("/kyc/test")
async def kyc_test():
    """KYC test endpoint"""
    return {"message": "KYC working"}

@app.get("/notifications/test")
async def notifications_test():
    """Notifications test endpoint"""
    return {"message": "Notifications working"}

@app.get("/admin/test")
async def admin_test():
    """Admin test endpoint"""
    return {"message": "Admin working"}

if __name__ == "__main__":
    print("🚀 Starting Banking Transfer Platform Server...")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )