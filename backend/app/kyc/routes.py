"""
KYC routes for Banking Transfer Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
import structlog

from app.common.database import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_user
from app.kyc.models import KYCDocument, DocumentType, KYCStatus

logger = structlog.get_logger()

router = APIRouter()

@router.get("/documents", response_model=dict)
async def get_kyc_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[KYCStatus] = None,
    document_type: Optional[DocumentType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KYC documents for current user"""
    try:
        # Mock KYC documents
        documents = [
            {
                "id": "doc123",
                "document_type": "passport",
                "file_name": "passport.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "status": "approved",
                "verified_at": "2023-11-16T14:30:00Z",
                "rejection_reason": None,
                "created_at": "2023-11-15T10:00:00Z"
            },
            {
                "id": "doc124",
                "document_type": "national_id",
                "file_name": "national_id.pdf",
                "file_size": 512000,
                "mime_type": "application/pdf",
                "status": "pending",
                "verified_at": None,
                "rejection_reason": None,
                "created_at": "2023-12-01T09:00:00Z"
            }
        ]
        
        # Filter by status if specified
        if status:
            documents = [d for d in documents if d["status"] == status.value]
        
        # Filter by document type if specified
        if document_type:
            documents = [d for d in documents if d["document_type"] == document_type.value]
        
        # Pagination
        total = len(documents)
        start = (page - 1) * size
        end = start + size
        paginated_documents = documents[start:end]
        
        return {
            "documents": paginated_documents,
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

@router.post("/documents/upload", response_model=dict)
async def upload_kyc_document(
    document_type: DocumentType,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload KYC document"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "image/jpeg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF, JPEG, and PNG are allowed"
            )
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Mock document upload
        document_id = f"doc{len(str(current_user.id))}"
        
        logger.info(f"KYC document uploaded: {document_id} for user {current_user.id}")
        
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload KYC document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )

@router.get("/documents/{document_id}", response_model=dict)
async def get_kyc_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KYC document details"""
    try:
        # Mock document details
        document = {
            "id": document_id,
            "document_type": "passport",
            "file_name": "passport.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "status": "approved",
            "verified_at": "2023-11-16T14:30:00Z",
            "rejection_reason": None,
            "created_at": "2023-11-15T10:00:00Z",
            "updated_at": "2023-11-16T14:30:00Z"
        }
        
        return document
        
    except Exception as e:
        logger.error(f"Failed to get KYC document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )

@router.delete("/documents/{document_id}", response_model=dict)
async def delete_kyc_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete KYC document"""
    try:
        # Mock document deletion
        logger.info(f"KYC document deleted: {document_id} for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete KYC document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

@router.get("/status", response_model=dict)
async def get_kyc_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KYC status for current user"""
    try:
        # Mock KYC status
        status_data = {
            "overall_status": "pending",
            "verification_level": "basic",
            "required_documents": [
                {
                    "type": "passport",
                    "status": "approved",
                    "uploaded": True
                },
                {
                    "type": "proof_of_address",
                    "status": "pending",
                    "uploaded": False
                }
            ],
            "checks": [
                {
                    "type": "sanctions",
                    "status": "passed",
                    "performed_at": "2023-11-16T14:30:00Z"
                },
                {
                    "type": "pep",
                    "status": "pending",
                    "performed_at": None
                }
            ],
            "risk_score": 0.2,
            "last_updated": "2023-12-01T10:00:00Z"
        }
        
        return status_data
        
    except Exception as e:
        logger.error(f"Failed to get KYC status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve KYC status"
        )

@router.post("/submit", response_model=dict)
async def submit_kyc(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit KYC for review"""
    try:
        # Mock KYC submission
        logger.info(f"KYC submitted for review: user {current_user.id}")
        
        return {
            "success": True,
            "message": "KYC submitted for review",
            "estimated_review_time": "2-3 business days"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit KYC: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit KYC"
        )