"""
Authentication routes for Banking Transfer Platform
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import structlog

from app.common.database import get_db
from app.auth.models import User, UserRoleAssignment, RefreshToken, LoginAttempt, PasswordReset, Session as UserSession
from app.auth.dependencies import get_current_user, get_current_active_user
from app.auth.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, UserUpdate
)
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            country_code=user_data.country_code
        )
        user.set_password(user_data.password)
        
        # Add default user role
        user_role = UserRoleAssignment(
            user_id=user.id,
            role="user"
        )
        
        db.add(user)
        db.add(user_role)
        db.commit()
        db.refresh(user)
        
        logger.info(f"New user registered: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            status=user.status,
            email_verified=user.email_verified,
            created_at=user.created_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == form_data.username).first()
        
        # Log login attempt
        login_attempt = LoginAttempt(
            user_id=user.id if user else None,
            email=form_data.username,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=False
        )
        
        # Validate user and password
        if not user or not user.verify_password(form_data.password):
            login_attempt.failure_reason = "invalid_credentials"
            db.add(login_attempt)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is locked
        if user.is_locked():
            login_attempt.failure_reason = "account_locked"
            db.add(login_attempt)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is locked due to too many failed attempts"
            )
        
        # Check if user is active
        if user.status != "active":
            login_attempt.failure_reason = "account_inactive"
            db.add(login_attempt)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Reset failed attempts on successful login
        user.reset_failed_attempts()
        user.last_login = datetime.utcnow()
        
        # Generate tokens
        settings = get_settings()
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.security.refresh_token_expire_days)
        
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            user_id=user.id,
            expires_delta=refresh_token_expires,
            db=db
        )
        
        # Log successful login
        login_attempt.success = True
        login_attempt.user_id = user.id
        
        db.add(login_attempt)
        db.commit()
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token.token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Find refresh token
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_data.refresh_token
        ).first()
        
        if not refresh_token or not refresh_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == refresh_token.user_id).first()
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        settings = get_settings()
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token.token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user and revoke refresh tokens"""
    try:
        # Revoke all refresh tokens for user
        db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked == False
        ).update({
            "revoked": True,
            "revoked_at": datetime.utcnow()
        })
        
        db.commit()
        
        logger.info(f"User logged out: {current_user.email}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == reset_data.email).first()
        if not user:
            # Don't reveal if user exists
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Create password reset token
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        password_reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(password_reset)
        db.commit()
        
        # TODO: Send email with reset link
        logger.info(f"Password reset requested for: {user.email}")
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset"""
    try:
        # Find password reset token
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.token == reset_data.token
        ).first()
        
        if not password_reset or not password_reset.is_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update user password
        user = db.query(User).filter(User.id == password_reset.user_id).first()
        user.set_password(reset_data.new_password)
        
        # Mark token as used
        password_reset.used = True
        password_reset.used_at = datetime.utcnow()
        
        # Revoke all refresh tokens
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False
        ).update({
            "revoked": True,
            "revoked_at": datetime.utcnow()
        })
        
        db.commit()
        
        logger.info(f"Password reset completed for: {user.email}")
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        status=current_user.status,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Update user fields
        if user_data.first_name:
            current_user.first_name = user_data.first_name
        if user_data.last_name:
            current_user.last_name = user_data.last_name
        if user_data.phone:
            current_user.phone = user_data.phone
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User updated: {current_user.email}")
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            phone=current_user.phone,
            status=current_user.status,
            email_verified=current_user.email_verified,
            created_at=current_user.created_at
        )
        
    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token"""
    settings = get_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt

def create_refresh_token(user_id: str, expires_delta: timedelta, db: Session):
    """Create refresh token"""
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + expires_delta
    
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(refresh_token)
    db.commit()
    
    return refresh_token