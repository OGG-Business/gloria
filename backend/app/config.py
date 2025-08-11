"""
Configuration settings for Banking Transfer Platform
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field

class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(default="postgresql://user:password@localhost:5432/banking_platform", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    class Config:
        env_prefix = "DB_"

class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Vault configuration
    vault_url: str = Field(default="http://localhost:8200", env="VAULT_URL")
    vault_token: str = Field(default="", env="VAULT_TOKEN")
    vault_mount_point: str = Field(default="secret", env="VAULT_MOUNT_POINT")
    
    class Config:
        env_prefix = "SECURITY_"

class SwiftSettings(BaseSettings):
    """SWIFT configuration"""
    bic: str = Field(default="TESTUS33XXX", env="SWIFT_BIC")
    cert_path: str = Field(default="/certs/client.crt", env="SWIFT_CERT_PATH")
    key_path: str = Field(default="/certs/client.key", env="SWIFT_KEY_PATH")
    ca_cert_path: str = Field(default="/certs/ca.crt", env="SWIFT_CA_CERT_PATH")
    endpoint: str = Field(default="https://test.swift.com", env="SWIFT_ENDPOINT")
    dry_run: bool = Field(default=True, env="SWIFT_DRY_RUN")
    
    class Config:
        env_prefix = "SWIFT_"

class MojaloopSettings(BaseSettings):
    """Mojaloop configuration"""
    endpoint: str = Field(default="https://test.mojaloop.io", env="MOJALOOP_ENDPOINT")
    participant_id: str = Field(default="test-participant", env="MOJALOOP_PARTICIPANT_ID")
    api_key: str = Field(default="test-api-key", env="MOJALOOP_API_KEY")
    dry_run: bool = Field(default=True, env="MOJALOOP_DRY_RUN")
    
    class Config:
        env_prefix = "MOJALOOP_"

class RedisSettings(BaseSettings):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    
    class Config:
        env_prefix = "REDIS_"

class NotificationSettings(BaseSettings):
    """Notification configuration"""
    smtp_host: str = Field(default="localhost", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # Twilio configuration
    twilio_account_sid: str = Field(default="", env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(default="", env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(default="", env="TWILIO_PHONE_NUMBER")
    
    # Firebase configuration
    firebase_credentials: str = Field(default="", env="FIREBASE_CREDENTIALS")
    
    class Config:
        env_prefix = "NOTIFICATION_"

class MonitoringSettings(BaseSettings):
    """Monitoring configuration"""
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Tracing configuration
    jaeger_host: str = Field(default="localhost", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    
    class Config:
        env_prefix = "MONITORING_"

class KYCSettings(BaseSettings):
    """KYC configuration"""
    transfer_limit_usd: float = Field(default=10000.0, env="KYC_TRANSFER_LIMIT_USD")
    sanctions_api_url: str = Field(default="", env="SANCTIONS_API_URL")
    sanctions_api_key: str = Field(default="", env="SANCTIONS_API_KEY")
    document_storage_path: str = Field(default="/uploads/kyc", env="KYC_DOCUMENT_STORAGE_PATH")
    
    class Config:
        env_prefix = "KYC_"

class Settings(BaseSettings):
    """Main application settings"""
    # Application
    app_name: str = Field(default="Banking Transfer Platform", env="APP_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    swift: SwiftSettings = SwiftSettings()
    mojaloop: MojaloopSettings = MojaloopSettings()
    redis: RedisSettings = RedisSettings()
    notifications: NotificationSettings = NotificationSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    kyc: KYCSettings = KYCSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings