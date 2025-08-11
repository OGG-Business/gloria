"""
Configuration settings for Banking Transfer Platform
"""

from typing import List, Optional
from pydantic import BaseSettings, Field
import os

class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(
        default="postgresql://banking_user:banking_password@localhost:5432/banking_transfer",
        env="DATABASE_URL"
    )
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")

class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Vault settings
    vault_addr: Optional[str] = Field(default=None, env="VAULT_ADDR")
    vault_token: Optional[str] = Field(default=None, env="VAULT_TOKEN")
    vault_mount_point: str = Field(default="secret", env="VAULT_MOUNT_POINT")

class SwiftSettings(BaseSettings):
    """SWIFT configuration"""
    bic: str = Field(default="TESTUS33XXX", env="SWIFT_BIC")
    endpoint: str = Field(default="https://test.swift.com", env="SWIFT_ENDPOINT")
    cert_path: Optional[str] = Field(default=None, env="SWIFT_CERT_PATH")
    key_path: Optional[str] = Field(default=None, env="SWIFT_KEY_PATH")
    ca_cert_path: Optional[str] = Field(default=None, env="SWIFT_CA_CERT_PATH")
    dry_run: bool = Field(default=True, env="SWIFT_DRY_RUN")
    timeout: int = Field(default=30, env="SWIFT_TIMEOUT")

class MojaloopSettings(BaseSettings):
    """Mojaloop configuration"""
    endpoint: str = Field(default="https://test.mojaloop.io", env="MOJALOOP_ENDPOINT")
    participant_id: str = Field(default="test-participant", env="MOJALOOP_PARTICIPANT_ID")
    api_key: str = Field(default="test-api-key", env="MOJALOOP_API_KEY")
    dry_run: bool = Field(default=True, env="MOJALOOP_DRY_RUN")
    timeout: int = Field(default=30, env="MOJALOOP_TIMEOUT")

class RedisSettings(BaseSettings):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")

class NotificationSettings(BaseSettings):
    """Notification configuration"""
    # SMTP settings
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Twilio settings
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    
    # Firebase settings
    firebase_credentials: Optional[str] = Field(default=None, env="FIREBASE_CREDENTIALS")

class MonitoringSettings(BaseSettings):
    """Monitoring configuration"""
    # Prometheus settings
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    prometheus_path: str = Field(default="/metrics", env="PROMETHEUS_PATH")
    
    # Jaeger settings
    jaeger_host: str = Field(default="localhost", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

class KYCSettings(BaseSettings):
    """KYC configuration"""
    max_transfer_amount: float = Field(default=10000.0, env="KYC_MAX_TRANSFER_AMOUNT")
    max_daily_amount: float = Field(default=50000.0, env="KYC_MAX_DAILY_AMOUNT")
    max_monthly_amount: float = Field(default=200000.0, env="KYC_MAX_MONTHLY_AMOUNT")
    document_storage_path: str = Field(default="/app/uploads", env="DOCUMENT_STORAGE_PATH")
    sanctions_api_url: Optional[str] = Field(default=None, env="SANCTIONS_API_URL")
    sanctions_api_key: Optional[str] = Field(default=None, env="SANCTIONS_API_KEY")

class Settings(BaseSettings):
    """Main application settings"""
    # Application settings
    app_name: str = Field(default="Banking Transfer Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS"
    )
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    swift: SwiftSettings = SwiftSettings()
    mojaloop: MojaloopSettings = MojaloopSettings()
    redis: RedisSettings = RedisSettings()
    notification: NotificationSettings = NotificationSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    kyc: KYCSettings = KYCSettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings