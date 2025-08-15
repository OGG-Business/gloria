from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    environment: str = "dev"
    session_secret: str = "dev-secret-change"

    # TLS
    tls_cert_path: str = "/certs/dev-cert.pem"
    tls_key_path: str = "/certs/dev-key.pem"

    # CORS
    cors_allowed_origins: List[str] = ["https://localhost:4443", "http://localhost:4443"]

    # Database
    database_url: str = "postgresql+psycopg://app:app@db:5432/app"

    # Vault
    vault_addr: str = "http://vault:8200"
    vault_token: str = "root"
    vault_transit_key: str = "payments-aes-gcm"

    # Keycloak / OIDC
    oidc_issuer_url: str = "http://keycloak:8080/realms/payments"
    oidc_audience: str = "payments-api"

    # ISO20022
    iso20022_xsd_dir: str | None = None

    # Connectors (SWIFT)
    connector_swift_mode: str = "dry-run"
    connector_swift_protocol: str = "REST"
    connector_swift_endpoint: str = "https://bank.example.com/as4"
    connector_swift_tls_client_cert_path: str = "/secrets/swift/client_cert.pem"
    connector_swift_tls_client_key_path: str = "/secrets/swift/client_key.pem"
    connector_swift_tls_ca_chain_path: str = "/secrets/swift/ca_chain.pem"
    connector_swift_username: str | None = None
    connector_swift_password: str | None = None

    # SFTP specifics
    connector_swift_sftp_host: str | None = None
    connector_swift_sftp_port: int = 22
    connector_swift_sftp_username: str | None = None
    connector_swift_sftp_password: str | None = None
    connector_swift_sftp_key_path: str | None = None
    connector_swift_sftp_remote_dir: str | None = None

    # Connectors (AZQORE Service Bureau)
    connector_azqore_api_url: str = "https://api.azqore.com"
    connector_azqore_bic: str = "SBXACHSS"

    # Keycloak Client for AZQORE Token
    keycloak_azqore_client_id: str | None = None
    keycloak_azqore_client_secret: str | None = None

    # PSD2 (BNP Paribas)
    psd2_base_url: str = "https://psd2.api.cib.bnpparibas.com"
    psd2_api_key_header_name: str = "AddAPIKey"
    psd2_api_key_value: str | None = None
    psd2_tls_client_cert_path: str = "/secrets/psd2/client_cert.pem"
    psd2_tls_client_key_path: str = "/secrets/psd2/client_key.pem"
    psd2_tls_ca_chain_path: str = "/secrets/psd2/ca_chain.pem"

    # AML/KYC
    aml_threshold_usd: float = 10000.0

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    return Settings()