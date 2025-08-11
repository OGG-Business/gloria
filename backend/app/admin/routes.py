"""
Admin routes for Banking Transfer Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.common.database import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_admin_user

logger = structlog.get_logger()

router = APIRouter()

@router.get("/dashboard", response_model=dict)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get admin dashboard data"""
    try:
        # Mock dashboard data
        dashboard_data = {
            "total_users": 1250,
            "active_users": 980,
            "total_transfers": 5670,
            "pending_transfers": 45,
            "total_volume": 1250000.00,
            "currency": "USD",
            "kyc_pending": 23,
            "security_alerts": 5,
            "system_health": {
                "database": "healthy",
                "redis": "healthy",
                "swift_connector": "healthy",
                "mojaloop_connector": "healthy"
            },
            "recent_activity": [
                {
                    "id": "1",
                    "type": "transfer_created",
                    "description": "New transfer created",
                    "timestamp": "2023-12-01T10:00:00Z",
                    "user_id": "user123"
                },
                {
                    "id": "2",
                    "type": "user_registered",
                    "description": "New user registered",
                    "timestamp": "2023-12-01T09:45:00Z",
                    "user_id": "user124"
                }
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get admin dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin dashboard"
        )

@router.get("/users", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get users for admin"""
    try:
        # Mock users data
        users = [
            {
                "id": "user123",
                "username": "john.doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "status": "active",
                "is_verified": True,
                "mfa_enabled": True,
                "created_at": "2023-11-01T10:00:00Z",
                "last_login": "2023-12-01T09:00:00Z",
                "roles": ["user"]
            },
            {
                "id": "user124",
                "username": "jane.smith",
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "status": "active",
                "is_verified": True,
                "mfa_enabled": False,
                "created_at": "2023-11-15T14:30:00Z",
                "last_login": "2023-12-01T08:30:00Z",
                "roles": ["user"]
            }
        ]
        
        # Filter by status if specified
        if status:
            users = [u for u in users if u["status"] == status]
        
        # Filter by role if specified
        if role:
            users = [u for u in users if role in u["roles"]]
        
        # Pagination
        total = len(users)
        start = (page - 1) * size
        end = start + size
        paginated_users = users[start:end]
        
        return {
            "users": paginated_users,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/transfers", response_model=dict)
async def get_transfers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    transfer_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get transfers for admin"""
    try:
        # Mock transfers data
        transfers = [
            {
                "id": "transfer123",
                "transfer_id": "TRF202312011000001",
                "user_id": "user123",
                "amount": 1000.00,
                "currency": "USD",
                "status": "completed",
                "transfer_type": "swift",
                "beneficiary_name": "John Smith",
                "created_at": "2023-12-01T10:00:00Z",
                "completed_at": "2023-12-01T10:05:00Z"
            },
            {
                "id": "transfer124",
                "transfer_id": "TRF202312011000002",
                "user_id": "user124",
                "amount": 500.00,
                "currency": "EUR",
                "status": "pending",
                "transfer_type": "iban",
                "beneficiary_name": "Jane Doe",
                "created_at": "2023-12-01T09:30:00Z",
                "completed_at": None
            }
        ]
        
        # Filter by status if specified
        if status:
            transfers = [t for t in transfers if t["status"] == status]
        
        # Filter by transfer type if specified
        if transfer_type:
            transfers = [t for t in transfers if t["transfer_type"] == transfer_type]
        
        # Pagination
        total = len(transfers)
        start = (page - 1) * size
        end = start + size
        paginated_transfers = transfers[start:end]
        
        return {
            "transfers": paginated_transfers,
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

@router.get("/kyc", response_model=dict)
async def get_kyc_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get KYC documents for admin"""
    try:
        # Mock KYC data
        kyc_documents = [
            {
                "id": "kyc123",
                "user_id": "user123",
                "document_type": "passport",
                "status": "approved",
                "file_name": "passport.pdf",
                "created_at": "2023-11-15T10:00:00Z",
                "verified_at": "2023-11-16T14:30:00Z",
                "verified_by": "admin1"
            },
            {
                "id": "kyc124",
                "user_id": "user124",
                "document_type": "national_id",
                "status": "pending",
                "file_name": "national_id.pdf",
                "created_at": "2023-12-01T09:00:00Z",
                "verified_at": None,
                "verified_by": None
            }
        ]
        
        # Filter by status if specified
        if status:
            kyc_documents = [k for k in kyc_documents if k["status"] == status]
        
        # Pagination
        total = len(kyc_documents)
        start = (page - 1) * size
        end = start + size
        paginated_documents = kyc_documents[start:end]
        
        return {
            "kyc_documents": paginated_documents,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get KYC documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KYC documents"
        )

@router.get("/audit-logs", response_model=dict)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get audit logs for admin"""
    try:
        # Mock audit logs
        audit_logs = [
            {
                "id": "audit123",
                "trace_id": "trace123",
                "user_id": "user123",
                "action": "transfer_created",
                "resource": "/transfers",
                "status": "success",
                "ip_address": "192.168.1.100",
                "created_at": "2023-12-01T10:00:00Z"
            },
            {
                "id": "audit124",
                "trace_id": "trace124",
                "user_id": "user124",
                "action": "login",
                "resource": "/auth/login",
                "status": "success",
                "ip_address": "192.168.1.101",
                "created_at": "2023-12-01T09:30:00Z"
            }
        ]
        
        # Filter by action if specified
        if action:
            audit_logs = [a for a in audit_logs if a["action"] == action]
        
        # Filter by user_id if specified
        if user_id:
            audit_logs = [a for a in audit_logs if a["user_id"] == user_id]
        
        # Pagination
        total = len(audit_logs)
        start = (page - 1) * size
        end = start + size
        paginated_logs = audit_logs[start:end]
        
        return {
            "audit_logs": paginated_logs,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )

@router.get("/system-metrics", response_model=dict)
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system metrics for admin"""
    try:
        # Mock system metrics
        metrics = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.4,
            "active_connections": 125,
            "database_connections": 15,
            "redis_connections": 8,
            "uptime": "15 days, 3 hours, 45 minutes",
            "last_backup": "2023-11-30T02:00:00Z",
            "security_alerts": 3,
            "performance_alerts": 1
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics"
        )