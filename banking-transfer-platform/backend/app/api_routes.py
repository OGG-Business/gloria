"""
API Routes pour Banking Transfer Platform
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import structlog
from datetime import datetime
from typing import Dict, Any

from app.common.database import get_db
from app.transfers.services import TransferService
from app.auth.models import User
from app.auth.dependencies import get_current_user

logger = structlog.get_logger()

api_router = APIRouter()

@api_router.post("/api/transfers")
async def create_transfer_api(
    transfer_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API endpoint pour créer un transfert SWIFT"""
    try:
        logger.info("Tentative de création de transfert via API", 
                   user_id=current_user.id, 
                   amount=transfer_data.get('amount'))
        
        transfer_service = TransferService(db)
        
        # Validation des données
        required_fields = ['amount', 'currency', 'recipient_iban', 'recipient_name']
        for field in required_fields:
            if field not in transfer_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Champ requis manquant: {field}"
                )
        
        # Créer le transfert
        transfer = await transfer_service.create_transfer(transfer_data, current_user)
        
        logger.info("Transfert créé avec succès via API",
                   transfer_id=transfer.transfer_id,
                   user_id=current_user.id)
        
        return {
            "success": True,
            "id": transfer.transfer_id,
            "status": "PENDING",
            "message": "Transfert initié avec succès",
            "timestamp": datetime.now().isoformat(),
            "transfer_details": {
                "amount": transfer.amount,
                "currency": transfer.currency,
                "recipient_iban": transfer.recipient_iban,
                "recipient_name": transfer.recipient_name,
                "swift_message_id": f"SWIFT{transfer.transfer_id}",
                "gpi_tracking_id": f"GPI{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création transfert via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la création du transfert"
        )

@api_router.get("/api/transfers")
async def get_transfers_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API endpoint pour récupérer les transferts"""
    try:
        transfer_service = TransferService(db)
        transfers, total = await transfer_service.get_user_transfers(current_user.id, 1, 50)
        
        return {
            "success": True,
            "transfers": [
                {
                    "id": t.transfer_id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "status": t.status.value,
                    "recipient_name": t.recipient_name,
                    "created_at": t.created_at.isoformat()
                }
                for t in transfers
            ],
            "total": total
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération transferts via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des transferts"
        )

@api_router.get("/api/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
