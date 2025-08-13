"""
Main FastAPI application for Banking Transfer Platform - SIMPLIFIED VERSION
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Banking Transfer Platform",
    description="A complete cloud-native platform for real bank transfers (SWIFT & IBAN)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Transfer Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/auth",
            "accounts": "/accounts", 
            "transfers": "/transfers",
            "kyc": "/kyc",
            "notifications": "/notifications",
            "admin": "/admin",
            "api": "/api"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "simulated",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# API Health endpoint
@app.get("/api/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# API Transfers endpoint (GET)
@app.get("/api/transfers")
async def get_transfers_api():
    """API endpoint pour récupérer les transferts"""
    return {
        "success": True,
        "transfers": [],
        "total": 0,
        "timestamp": datetime.now().isoformat()
    }

# API Transfers endpoint (POST)
@app.post("/api/transfers")
async def create_transfer_api(transfer_data: dict):
    """API endpoint pour créer un transfert SWIFT"""
    try:
        # Validation des données
        required_fields = ['amount', 'currency', 'recipient_iban', 'recipient_name']
        for field in required_fields:
            if field not in transfer_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Champ requis manquant: {field}"
                )
        
        # Simulation de création de transfert
        transfer_id = f"TRANSFER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True,
            "id": transfer_id,
            "status": "PENDING",
            "message": "Transfert initié avec succès",
            "timestamp": datetime.now().isoformat(),
            "transfer_details": {
                "amount": transfer_data.get('amount'),
                "currency": transfer_data.get('currency'),
                "recipient_iban": transfer_data.get('recipient_iban'),
                "recipient_name": transfer_data.get('recipient_name'),
                "swift_message_id": f"SWIFT{transfer_id}",
                "gpi_tracking_id": f"GPI{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la création du transfert"
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
