"""
Transfer API Routes
Handles transfer creation, retrieval, and management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.common.database import get_db
from app.auth.dependencies import get_current_user
from app.transfers.models import Transfer, TransferStatus, TransferPriority, TransferType
from app.transfers.services import TransferService
from app.accounts.models import Account
from app.common.exceptions import TransferError, InsufficientFundsError, ValidationError

router = APIRouter(prefix="/transfers", tags=["transfers"])

# Request/Response Models
class CreateTransferRequest(BaseModel):
    source_account_id: str = Field(..., description="Source account ID")
    beneficiary_name: str = Field(..., description="Beneficiary name")
    beneficiary_iban: str = Field(..., description="Beneficiary IBAN")
    beneficiary_bic: str = Field(..., description="Beneficiary BIC")
    amount: float = Field(..., gt=0, description="Transfer amount")
    currency: str = Field(..., description="Currency code")
    description: str = Field(..., description="Transfer description")
    priority: TransferPriority = Field(TransferPriority.NORMAL, description="Transfer priority")
    transfer_type: TransferType = Field(..., description="Transfer type")

class TransferResponse(BaseModel):
    id: str
    transfer_id: str
    amount: float
    currency: str
    source_account_id: str
    destination_account_id: str
    beneficiary_name: str
    beneficiary_iban: str
    beneficiary_bic: str
    description: str
    status: TransferStatus
    priority: TransferPriority
    transfer_type: TransferType
    fees: float
    exchange_rate: Optional[float]
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    swift_message_id: Optional[str]
    mojaloop_transfer_id: Optional[str]

    class Config:
        from_attributes = True

@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    request: CreateTransferRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transfer"""
    try:
        transfer_service = TransferService(db)
        transfer = await transfer_service.create_transfer(
            user_id=current_user.id,
            transfer_data=request.dict()
        )
        return TransferResponse.from_orm(transfer)
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds: {str(e)}"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except TransferError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer creation failed: {str(e)}"
        )

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[TransferStatus] = Query(None, description="Filter by status"),
    transfer_type: Optional[TransferType] = Query(None, description="Filter by transfer type"),
    priority: Optional[TransferPriority] = Query(None, description="Filter by priority"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transfers with filtering and pagination"""
    try:
        transfer_service = TransferService(db)
        filters = {
            "status": status,
            "transfer_type": transfer_type,
            "priority": priority,
            "currency": currency
        }
        
        transfers = await transfer_service.get_transfers(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            filters=filters
        )
        
        return [TransferResponse.from_orm(transfer) for transfer in transfers]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transfers: {str(e)}"
        )

@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transfer by ID"""
    try:
        transfer_service = TransferService(db)
        transfer = await transfer_service.get_transfer(
            transfer_id=transfer_id,
            user_id=current_user.id
        )
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        return TransferResponse.from_orm(transfer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transfer: {str(e)}"
        )

@router.post("/{transfer_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_transfer(
    transfer_id: str,
    reason: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a transfer"""
    try:
        transfer_service = TransferService(db)
        await transfer_service.cancel_transfer(
            transfer_id=transfer_id,
            user_id=current_user.id,
            reason=reason
        )
        
        return {"message": "Transfer cancelled successfully"}
    except TransferError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel transfer: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel transfer: {str(e)}"
        )