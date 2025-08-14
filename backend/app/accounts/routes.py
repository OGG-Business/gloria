"""
Account routes for Banking Transfer Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog
from sqlalchemy import and_

from app.common.database import get_db
from app.accounts.models import Account, AccountActivity, AccountStatus, AccountType, Currency
from app.auth.models import User
from app.auth.dependencies import get_current_user

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=dict)
async def get_accounts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[AccountStatus] = None,
    account_type: Optional[AccountType] = None,
    currency: Optional[Currency] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get accounts for current user"""
    try:
        query = db.query(Account).filter(Account.user_id == current_user.id)
        
        if status:
            query = query.filter(Account.status == status)
        
        if account_type:
            query = query.filter(Account.account_type == account_type)
        
        if currency:
            query = query.filter(Account.currency == currency)
        
        total = query.count()
        accounts = query.order_by(Account.created_at.desc()).offset((page - 1) * size).limit(size).all()
        
        return {
            "accounts": [
                {
                    "id": account.id,
                    "account_number": account.account_number,
                    "iban": account.iban,
                    "bic": account.bic,
                    "holder_name": account.holder_name,
                    "balance": account.balance,
                    "available_balance": account.available_balance,
                    "blocked_amount": account.blocked_amount,
                    "currency": account.currency.value,
                    "account_type": account.account_type.value,
                    "status": account.status.value,
                    "daily_limit": account.daily_limit,
                    "monthly_limit": account.monthly_limit,
                    "daily_used": account.daily_used,
                    "monthly_used": account.monthly_used,
                    "created_at": account.created_at.isoformat(),
                    "is_active": account.is_active,
                    "can_transfer": account.can_transfer
                }
                for account in accounts
            ],
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounts"
        )

@router.get("/{account_id}", response_model=dict)
async def get_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get account details"""
    try:
        account = db.query(Account).filter(
            and_(
                Account.id == account_id,
                Account.user_id == current_user.id
            )
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return {
            "id": account.id,
            "account_number": account.account_number,
            "iban": account.iban,
            "bic": account.bic,
            "holder_name": account.holder_name,
            "balance": account.balance,
            "available_balance": account.available_balance,
            "blocked_amount": account.blocked_amount,
            "currency": account.currency.value,
            "account_type": account.account_type.value,
            "status": account.status.value,
            "daily_limit": account.daily_limit,
            "monthly_limit": account.monthly_limit,
            "daily_used": account.daily_used,
            "monthly_used": account.monthly_used,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat() if account.updated_at else None,
            "is_active": account.is_active,
            "can_transfer": account.can_transfer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account"
        )

@router.get("/{account_id}/activity", response_model=dict)
async def get_account_activity(
    account_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get account activity"""
    try:
        # Verify account belongs to user
        account = db.query(Account).filter(
            and_(
                Account.id == account_id,
                Account.user_id == current_user.id
            )
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        query = db.query(AccountActivity).filter(AccountActivity.account_id == account_id)
        total = query.count()
        activities = query.order_by(AccountActivity.created_at.desc()).offset((page - 1) * size).limit(size).all()
        
        return {
            "account_id": account_id,
            "activities": [
                {
                    "id": activity.id,
                    "activity_type": activity.activity_type,
                    "amount": activity.amount,
                    "currency": activity.currency.value,
                    "description": activity.description,
                    "reference": activity.reference,
                    "balance_before": activity.balance_before,
                    "balance_after": activity.balance_after,
                    "created_at": activity.created_at.isoformat()
                }
                for activity in activities
            ],
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account activity for {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account activity"
        )

@router.get("/{account_id}/balance", response_model=dict)
async def get_account_balance(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get account balance"""
    try:
        account = db.query(Account).filter(
            and_(
                Account.id == account_id,
                Account.user_id == current_user.id
            )
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return {
            "account_id": account.id,
            "account_number": account.account_number,
            "balance": account.balance,
            "available_balance": account.available_balance,
            "blocked_amount": account.blocked_amount,
            "currency": account.currency.value,
            "last_updated": account.updated_at.isoformat() if account.updated_at else account.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account balance for {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account balance"
        )

@router.get("/{account_id}/limits", response_model=dict)
async def get_account_limits(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get account transfer limits"""
    try:
        account = db.query(Account).filter(
            and_(
                Account.id == account_id,
                Account.user_id == current_user.id
            )
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return {
            "account_id": account.id,
            "daily_limit": account.daily_limit,
            "monthly_limit": account.monthly_limit,
            "daily_used": account.daily_used,
            "monthly_used": account.monthly_used,
            "daily_remaining": account.daily_limit - account.daily_used,
            "monthly_remaining": account.monthly_limit - account.monthly_used,
            "currency": account.currency.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account limits for {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account limits"
        )

@router.get("/summary", response_model=dict)
async def get_accounts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get accounts summary"""
    try:
        accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
        
        total_balance = sum(account.balance for account in accounts)
        total_available = sum(account.available_balance for account in accounts)
        total_blocked = sum(account.blocked_amount for account in accounts)
        
        accounts_by_currency = {}
        for account in accounts:
            currency = account.currency.value
            if currency not in accounts_by_currency:
                accounts_by_currency[currency] = {
                    "balance": 0,
                    "available_balance": 0,
                    "blocked_amount": 0,
                    "count": 0
                }
            
            accounts_by_currency[currency]["balance"] += account.balance
            accounts_by_currency[currency]["available_balance"] += account.available_balance
            accounts_by_currency[currency]["blocked_amount"] += account.blocked_amount
            accounts_by_currency[currency]["count"] += 1
        
        return {
            "total_accounts": len(accounts),
            "active_accounts": len([a for a in accounts if a.is_active]),
            "total_balance": total_balance,
            "total_available_balance": total_available,
            "total_blocked_amount": total_blocked,
            "accounts_by_currency": accounts_by_currency
        }
        
    except Exception as e:
        logger.error(f"Failed to get accounts summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounts summary"
        )