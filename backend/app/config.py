from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    app_env: str = Field(default="dev")
    auth_disabled: bool = Field(default=True)
    oidc_issuer: Optional[str] = None
    oidc_audience: Optional[str] = None

    database_url: str = Field(default="postgresql://postgres:postgres@db:5432/transfers")
    use_db: bool = Field(default=False)

    encryption_key_hex: Optional[str] = None  # 32 bytes hex for AES-256

    # Vault
    vault_addr: Optional[str] = None
    vault_token: Optional[str] = None
    vault_transit_key: Optional[str] = None

    # Notifications
    enable_sse: bool = Field(default=True)

    # Connectors
    swift_base_url: Optional[str] = None
    swift_client_cert: Optional[str] = None
    swift_client_key: Optional[str] = None
    swift_ca_cert: Optional[str] = None
    mojaloop_base_url: Optional[str] = None

    # Policy
    block_threshold_usd: float = Field(default=10000.0)

    # Mode
    dry_run: bool = Field(default=True)

    # Cloud SQL (for Cloud Run)
    db_instance_connection_name: Optional[str] = None

    class Config:
        env_prefix = "APP_"
        env_file = ".env"


settings = Settings()