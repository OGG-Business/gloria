import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Open Payments Hub"
    environment: str = os.environ.get("ENVIRONMENT", "dev")
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"

    # Database
    database_url: str = os.environ.get("DATABASE_URL", "postgresql://payment:payment@postgres:5432/payments")

    # Auth / OIDC
    oidc_issuer: Optional[str] = os.environ.get("OIDC_ISSUER")
    oidc_audience: Optional[str] = os.environ.get("OIDC_AUDIENCE")
    oidc_jwks_url: Optional[str] = os.environ.get("OIDC_JWKS_URL")
    dev_mode_no_auth: bool = os.environ.get("DEV_MODE_NO_AUTH", "true").lower() == "true"

    # Encryption / Secrets
    secrets_backend: str = os.environ.get("SECRETS_BACKEND", "env")  # env|vault|gsm
    app_master_key_b64: Optional[str] = os.environ.get("APP_MASTER_KEY")  # base64 key if secrets_backend=env

    # Vault
    vault_addr: Optional[str] = os.environ.get("VAULT_ADDR")
    vault_token: Optional[str] = os.environ.get("VAULT_TOKEN")
    vault_kv_path: Optional[str] = os.environ.get("VAULT_KV_PATH", "secret/data/open-payments-hub")
    vault_key_field: str = os.environ.get("VAULT_KEY_FIELD", "app_master_key")

    # Google Secret Manager
    gcp_project_id: Optional[str] = os.environ.get("GCP_PROJECT_ID")
    gsm_secret_name: Optional[str] = os.environ.get("GSM_SECRET_NAME", "app-master-key")

    # Pub/Sub Notifications
    pubsub_enabled: bool = os.environ.get("PUBSUB_ENABLED", "false").lower() == "true"
    pubsub_project_id: Optional[str] = os.environ.get("PUBSUB_PROJECT_ID")
    pubsub_topic_id: Optional[str] = os.environ.get("PUBSUB_TOPIC_ID")

    # Transfers / Compliance
    aml_block_threshold_usd: float = float(os.environ.get("AML_BLOCK_THRESHOLD_USD", "10000"))
    dry_run: bool = os.environ.get("DRY_RUN", "true").lower() == "true"
    bank_approval: str = os.environ.get("BANK_APPROVAL", "no")

    # Observability
    otlp_endpoint: Optional[str] = os.environ.get("OTLP_ENDPOINT")

    # Connectors
    swift_mode: str = os.environ.get("SWIFT_MODE", "dry")  # dry|rest|sftp|as4
    swift_rest_base_url: Optional[str] = os.environ.get("SWIFT_REST_BASE_URL")
    swift_rest_mtls: bool = os.environ.get("SWIFT_REST_MTLS", "false").lower() == "true"
    swift_client_cert_path: Optional[str] = os.environ.get("SWIFT_CLIENT_CERT_PATH")
    swift_client_key_path: Optional[str] = os.environ.get("SWIFT_CLIENT_KEY_PATH")
    swift_ca_cert_path: Optional[str] = os.environ.get("SWIFT_CA_CERT_PATH")

    mojaloop_base_url: Optional[str] = os.environ.get("MOJALOOP_BASE_URL")


settings = Settings()