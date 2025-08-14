"""
Transfer routes for Banking Transfer Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import structlog

from app.common.database import get_db
from app.transfers.services import TransferService
from app.transfers.models import Transfer, TransferStatus, TransferType, TransferPriority
from app.auth.models import User
from app.auth.dependencies import get_current_user

logger = structlog.get_logger()

router = APIRouter()

@router.post("/", response_model=dict)
async def create_transfer(
    transfer_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transfer"""
    try:
        transfer_service = TransferService(db)
        transfer = await transfer_service.create_transfer(transfer_data, current_user)
        
        logger.info(
            "Transfer created successfully",
            transfer_id=transfer.transfer_id,
            user_id=current_user.id,
            amount=transfer.amount,
            currency=transfer.currency
        )
        
        return {
            "success": True,
            "transfer_id": transfer.transfer_id,
            "status": transfer.status.value,
            "message": "Transfer created successfully"
        }
        
    except ValueError as e:
        logger.warning(f"Transfer creation failed - validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Transfer creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transfer"
        )

@router.get("/", response_model=dict)
async def get_transfers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[TransferStatus] = None,
    transfer_type: Optional[TransferType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transfers for current user"""
    try:
        transfer_service = TransferService(db)
        transfers, total = await transfer_service.get_user_transfers(
            current_user.id, page, size, status, transfer_type
        )
        
        return {
            "transfers": [
                {
                    "id": t.id,
                    "transfer_id": t.transfer_id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "status": t.status.value,
                    "transfer_type": t.transfer_type.value,
                    "beneficiary_name": t.beneficiary_name,
                    "created_at": t.created_at.isoformat(),
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None
                }
                for t in transfers
            ],
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get transfers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transfers"
        )

@router.get("/{transfer_id}", response_model=dict)
async def get_transfer(
    transfer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transfer details"""
    try:
        transfer_service = TransferService(db)
        transfer = await transfer_service.get_transfer(transfer_id, current_user.id)
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        return {
            "id": transfer.id,
            "transfer_id": transfer.transfer_id,
            "amount": transfer.amount,
            "currency": transfer.currency,
            "fees": transfer.fees,
            "total_amount": transfer.total_amount,
            "status": transfer.status.value,
            "transfer_type": transfer.transfer_type.value,
            "priority": transfer.priority.value,
            "beneficiary_name": transfer.beneficiary_name,
            "beneficiary_iban": transfer.beneficiary_iban,
            "beneficiary_bic": transfer.beneficiary_bic,
            "beneficiary_bank": transfer.beneficiary_bank,
            "description": transfer.description,
            "reference": transfer.reference,
            "created_at": transfer.created_at.isoformat(),
            "updated_at": transfer.updated_at.isoformat() if transfer.updated_at else None,
            "completed_at": transfer.completed_at.isoformat() if transfer.completed_at else None,
            "source_account": {
                "id": transfer.source_account.id,
                "account_number": transfer.source_account.account_number,
                "iban": transfer.source_account.iban,
                "holder_name": transfer.source_account.holder_name
            } if transfer.source_account else None,
            "destination_account": {
                "id": transfer.destination_account.id,
                "account_number": transfer.destination_account.account_number,
                "iban": transfer.destination_account.iban,
                "holder_name": transfer.destination_account.holder_name
            } if transfer.destination_account else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transfer {transfer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transfer"
        )

@router.get("/{transfer_id}/events", response_model=dict)
async def get_transfer_events(
    transfer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transfer events"""
    try:
        transfer_service = TransferService(db)
        transfer = await transfer_service.get_transfer(transfer_id, current_user.id)
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        events = [
            {
                "id": event.id,
                "event_type": event.event_type,
                "status": event.status.value,
                "description": event.description,
                "created_at": event.created_at.isoformat()
            }
            for event in transfer.events
        ]
        
        return {
            "transfer_id": transfer_id,
            "events": events
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transfer events for {transfer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transfer events"
        )

@router.post("/{transfer_id}/cancel", response_model=dict)
async def cancel_transfer(
    transfer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a transfer"""
    try:
        transfer_service = TransferService(db)
        success = await transfer_service.cancel_transfer(transfer_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer cannot be cancelled"
            )
        
        logger.info(
            "Transfer cancelled successfully",
            transfer_id=transfer_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "message": "Transfer cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel transfer {transfer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel transfer"
        )

@router.get("/status/{transfer_id}", response_model=dict)
async def get_transfer_status(
    transfer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transfer status"""
    try:
        transfer_service = TransferService(db)
        transfer = await transfer_service.get_transfer(transfer_id, current_user.id)
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        return {
            "transfer_id": transfer.transfer_id,
            "status": transfer.status.value,
            "is_completed": transfer.is_completed,
            "is_failed": transfer.is_failed,
            "is_pending": transfer.is_pending,
            "can_cancel": transfer.can_cancel,
            "last_updated": transfer.updated_at.isoformat() if transfer.updated_at else transfer.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transfer status for {transfer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transfer status"
        )

@router.post("/validate", response_model=dict)
async def validate_transfer(
    transfer_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate transfer data before creation"""
    try:
        transfer_service = TransferService(db)
        validation_result = await transfer_service.validate_transfer(transfer_data, current_user)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "estimated_fees": validation_result.get("estimated_fees", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Transfer validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate transfer"
        )