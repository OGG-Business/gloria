"""
Configuration principale de l'application Banking Transfer Platform
"""
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings
import os


class DatabaseSettings(BaseSettings):
    """Configuration de la base de données"""
    url: str = Field(default="postgresql://user:pass@localhost:5432/banking", env="DATABASE_URL")
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    class Config:
        env_prefix = "DB_"


class SecuritySettings(BaseSettings):
    """Configuration de sécurité"""
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Vault configuration
    vault_addr: str = Field(default="http://localhost:8200", env="VAULT_ADDR")
    vault_token: Optional[str] = Field(default=None, env="VAULT_TOKEN")
    vault_mount_point: str = Field(default="secret", env="VAULT_MOUNT_POINT")
    
    # Encryption
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    class Config:
        env_prefix = "SECURITY_"


class SwiftSettings(BaseSettings):
    """Configuration SWIFT"""
    bic: str = Field(..., env="SWIFT_BIC")
    cert_path: str = Field(..., env="SWIFT_CERT_PATH")
    key_path: str = Field(..., env="SWIFT_KEY_PATH")
    endpoint: str = Field(..., env="SWIFT_ENDPOINT")
    timeout: int = Field(default=30, env="SWIFT_TIMEOUT")
    dry_run: bool = Field(default=True, env="SWIFT_DRY_RUN")
    
    # TLS Configuration
    tls_verify: bool = Field(default=True, env="SWIFT_TLS_VERIFY")
    tls_version: str = Field(default="1.3", env="SWIFT_TLS_VERSION")
    
    class Config:
        env_prefix = "SWIFT_"


class MojaloopSettings(BaseSettings):
    """Configuration Mojaloop"""
    endpoint: str = Field(default="https://mojaloop.example.com", env="MOJALOOP_ENDPOINT")
    api_key: Optional[str] = Field(default=None, env="MOJALOOP_API_KEY")
    timeout: int = Field(default=30, env="MOJALOOP_TIMEOUT")
    dry_run: bool = Field(default=True, env="MOJALOOP_DRY_RUN")
    
    class Config:
        env_prefix = "MOJALOOP_"


class RedisSettings(BaseSettings):
    """Configuration Redis"""
    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    
    class Config:
        env_prefix = "REDIS_"


class NotificationSettings(BaseSettings):
    """Configuration des notifications"""
    # Email
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(..., env="SMTP_USER")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    
    # SMS (Twilio)
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_from_number: Optional[str] = Field(default=None, env="TWILIO_FROM_NUMBER")
    
    # Push notifications
    firebase_credentials: Optional[str] = Field(default=None, env="FIREBASE_CREDENTIALS")
    
    class Config:
        env_prefix = "NOTIFICATION_"


class MonitoringSettings(BaseSettings):
    """Configuration du monitoring"""
    # Prometheus
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Tracing
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    class Config:
        env_prefix = "MONITORING_"


class KYCSettings(BaseSettings):
    """Configuration KYC/AML"""
    # Limites de montant
    max_transfer_amount: float = Field(default=10000.0, env="KYC_MAX_TRANSFER_AMOUNT")
    max_daily_amount: float = Field(default=50000.0, env="KYC_MAX_DAILY_AMOUNT")
    
    # Screening
    sanctions_api_url: Optional[str] = Field(default=None, env="SANCTIONS_API_URL")
    sanctions_api_key: Optional[str] = Field(default=None, env="SANCTIONS_API_KEY")
    
    # Document storage
    document_storage_path: str = Field(default="/tmp/documents", env="DOCUMENT_STORAGE_PATH")
    
    class Config:
        env_prefix = "KYC_"


class Settings(BaseSettings):
    """Configuration principale"""
    # Application
    app_name: str = Field(default="Banking Transfer Platform", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    swift: SwiftSettings = SwiftSettings()
    mojaloop: MojaloopSettings = MojaloopSettings()
    redis: RedisSettings = RedisSettings()
    notifications: NotificationSettings = NotificationSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    kyc: KYCSettings = KYCSettings()
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instance globale des paramètres
settings = Settings()


def get_settings() -> Settings:
    """Retourne l'instance des paramètres"""
    return settings