"""
Pydantic schemas for authentication
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., min_length=1, max_length=100, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User last name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    country_code: str = Field(..., min_length=2, max_length=2, description="Country code")

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    mfa_code: Optional[str] = Field(None, description="MFA code if enabled")

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    phone: Optional[str] = Field(None, description="User phone number")
    status: str = Field(..., description="User status")
    email_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation date")
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

class UserUpdate(BaseModel):
    """Schema for user update"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User last name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")

class ChangePasswordRequest(BaseModel):
    """Schema for password change"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class MFAEnableRequest(BaseModel):
    """Schema for MFA enable request"""
    mfa_code: str = Field(..., description="MFA verification code")

class MFADisableRequest(BaseModel):
    """Schema for MFA disable request"""
    mfa_code: str = Field(..., description="MFA verification code")
    password: str = Field(..., description="User password for confirmation")