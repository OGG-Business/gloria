"""
Account API Routes
Handles account management and balance operations
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.common.database import get_db
from app.auth.dependencies import get_current_user
from app.accounts.models import Account, AccountStatus, AccountType
from app.accounts.services import AccountService
from app.common.exceptions import AccountError, ValidationError

router = APIRouter(prefix="/accounts", tags=["accounts"])

# Request/Response Models
class AccountResponse(BaseModel):
    id: str
    account_number: str
    iban: str
    bic: str
    holder_name: str
    balance: float
    currency: str
    status: AccountStatus
    account_type: AccountType
    daily_limit: float
    monthly_limit: float
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class CreateAccountRequest(BaseModel):
    account_type: AccountType = Field(..., description="Account type")
    currency: str = Field(..., description="Currency code")
    holder_name: str = Field(..., description="Account holder name")
    daily_limit: float = Field(..., gt=0, description="Daily transfer limit")
    monthly_limit: float = Field(..., gt=0, description="Monthly transfer limit")

class UpdateAccountRequest(BaseModel):
    holder_name: Optional[str] = Field(None, description="Account holder name")
    daily_limit: Optional[float] = Field(None, gt=0, description="Daily transfer limit")
    monthly_limit: Optional[float] = Field(None, gt=0, description="Monthly transfer limit")
    status: Optional[AccountStatus] = Field(None, description="Account status")

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    status: Optional[AccountStatus] = Query(None, description="Filter by status"),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user accounts with filtering"""
    try:
        account_service = AccountService(db)
        filters = {
            "status": status,
            "account_type": account_type,
            "currency": currency
        }
        
        accounts = await account_service.get_user_accounts(
            user_id=current_user.id,
            filters=filters
        )
        
        return [AccountResponse.from_orm(account) for account in accounts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve accounts: {str(e)}"
        )

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific account by ID"""
    try:
        account_service = AccountService(db)
        account = await account_service.get_account(
            account_id=account_id,
            user_id=current_user.id
        )
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return AccountResponse.from_orm(account)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve account: {str(e)}"
        )

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: CreateAccountRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    try:
        account_service = AccountService(db)
        account = await account_service.create_account(
            user_id=current_user.id,
            account_data=request.dict()
        )
        return AccountResponse.from_orm(account)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except AccountError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account creation failed: {str(e)}"
        )

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    request: UpdateAccountRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an account"""
    try:
        account_service = AccountService(db)
        account = await account_service.update_account(
            account_id=account_id,
            user_id=current_user.id,
            account_data=request.dict(exclude_unset=True)
        )
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return AccountResponse.from_orm(account)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except AccountError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account update failed: {str(e)}"
        )

@router.post("/{account_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_account(
    account_id: str,
    reason: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Suspend an account"""
    try:
        account_service = AccountService(db)
        await account_service.suspend_account(
            account_id=account_id,
            user_id=current_user.id,
            reason=reason
        )
        
        return {"message": "Account suspended successfully"}
    except AccountError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot suspend account: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suspend account: {str(e)}"
        )

@router.post("/{account_id}/activate", status_code=status.HTTP_200_OK)
async def activate_account(
    account_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a suspended account"""
    try:
        account_service = AccountService(db)
        await account_service.activate_account(
            account_id=account_id,
            user_id=current_user.id
        )
        
        return {"message": "Account activated successfully"}
    except AccountError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot activate account: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate account: {str(e)}"
        )

@router.get("/{account_id}/activity")
async def get_account_activity(
    account_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get account activity/transaction history"""
    try:
        account_service = AccountService(db)
        activity = await account_service.get_account_activity(
            account_id=account_id,
            user_id=current_user.id,
            page=page,
            per_page=per_page
        )
        
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve account activity: {str(e)}"
        )

@router.get("/{account_id}/balance")
async def get_account_balance(
    account_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get account balance"""
    try:
        account_service = AccountService(db)
        balance = await account_service.get_account_balance(
            account_id=account_id,
            user_id=current_user.id
        )
        
        return {
            "account_id": account_id,
            "balance": balance,
            "currency": "USD",  # This should come from the account
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve account balance: {str(e)}"
        )