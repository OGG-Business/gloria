"""
Authentication routes for Banking Transfer Platform
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import structlog
from sqlalchemy import and_
import uuid

from app.common.database import get_db
from app.auth.models import User, RefreshToken, LoginAttempt, UserRole
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.security.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Create refresh token"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.security.refresh_token_expire_days)
    to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

@router.post("/login", response_model=dict)
async def login(
    request: Request,
    username: str,
    password: str,
    mfa_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """User login"""
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        
        # Log login attempt
        login_attempt = LoginAttempt(
            id=str(uuid.uuid4()),
            user_id=user.id if user else None,
            username=username,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent"),
            success=False,
            failure_reason="Invalid credentials"
        )
        
        if not user:
            db.add(login_attempt)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Check if user is locked
        if user.is_locked:
            login_attempt.failure_reason = "Account locked"
            db.add(login_attempt)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is locked"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                login_attempt.failure_reason = "Account locked due to too many failed attempts"
            else:
                login_attempt.failure_reason = "Invalid password"
            
            db.add(login_attempt)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Check MFA if enabled
        if user.mfa_enabled:
            if not mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MFA code required"
                )
            
            # Verify MFA code (simplified - in production use proper MFA library)
            if mfa_code != "123456":  # Mock MFA code
                login_attempt.failure_reason = "Invalid MFA code"
                db.add(login_attempt)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )
        
        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": user.id}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(user.id)
        
        # Save refresh token
        db_refresh_token = RefreshToken(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.security.refresh_token_expire_days),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Update login attempt
        login_attempt.success = True
        login_attempt.failure_reason = None
        
        db.add(db_refresh_token)
        db.add(login_attempt)
        db.commit()
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.security.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "mfa_enabled": user.mfa_enabled,
                "roles": [role.role.value for role in user.roles if role.is_active]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists and is valid
        db_refresh_token = db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == refresh_token,
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        ).first()
        
        if not db_refresh_token or not db_refresh_token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": user.id}, expires_delta=access_token_expires)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.security.access_token_expire_minutes * 60
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout", response_model=dict)
async def logout(
    refresh_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """User logout"""
    try:
        # Revoke refresh token
        db_refresh_token = db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == refresh_token,
                RefreshToken.user_id == current_user.id
            )
        ).first()
        
        if db_refresh_token:
            db_refresh_token.is_revoked = True
            db_refresh_token.revoked_at = datetime.now(timezone.utc)
            db.commit()
        
        logger.info(f"User logged out: {current_user.username}")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "status": current_user.status.value,
        "roles": [role.role.value for role in current_user.roles if role.is_active],
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "created_at": current_user.created_at.isoformat()
    }

@router.post("/change-password", response_model=dict)
async def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        
        # Update password
        current_user.hashed_password = hashed_password
        current_user.password_changed_at = datetime.now(timezone.utc)
        
        # Revoke all refresh tokens
        db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == current_user.id,
                RefreshToken.is_revoked == False
            )
        ).update({
            "is_revoked": True,
            "revoked_at": datetime.now(timezone.utc)
        })
        
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/enable-mfa", response_model=dict)
async def enable_mfa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable MFA for user"""
    try:
        if current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled"
            )
        
        # Generate MFA secret (in production, use proper MFA library)
        import secrets
        mfa_secret = secrets.token_hex(16)
        
        current_user.mfa_enabled = True
        current_user.mfa_secret = mfa_secret
        
        db.commit()
        
        logger.info(f"MFA enabled for user: {current_user.username}")
        
        return {
            "message": "MFA enabled successfully",
            "mfa_secret": mfa_secret  # In production, show QR code instead
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA enable failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable MFA"
        )

@router.post("/disable-mfa", response_model=dict)
async def disable_mfa(
    mfa_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disable MFA for user"""
    try:
        if not current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled"
            )
        
        # Verify MFA code (simplified)
        if mfa_code != "123456":  # Mock MFA code
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code"
            )
        
        current_user.mfa_enabled = False
        current_user.mfa_secret = None
        
        db.commit()
        
        logger.info(f"MFA disabled for user: {current_user.username}")
        
        return {"message": "MFA disabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA disable failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA"
        )