from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import BaseModel

class Settings(BaseSettings):
    # App
    environment: str = "dev"
    session_secret: str = "dev-secret-change"

    # TLS
    tls_cert_path: str = "/certs/dev-cert.pem"
    tls_key_path: str = "/certs/dev-key.pem"

    # Database
    database_url: str = "postgresql+psycopg://app:app@db:5432/app"

    # Vault
    vault_addr: str = "http://vault:8200"
    vault_token: str = "root"
    vault_transit_key: str = "payments-aes-gcm"

    # Keycloak / OIDC
    oidc_issuer_url: str = "http://keycloak:8080/realms/payments"
    oidc_audience: str = "payments-api"

    # Connectors
    connector_swift_mode: str = "dry-run"  # dry-run | live
    connector_swift_endpoint: str = "https://bank.example.com/as4"
    connector_swift_tls_client_cert_path: str = "/secrets/swift/client_cert.pem"
    connector_swift_tls_client_key_path: str = "/secrets/swift/client_key.pem"
    connector_swift_tls_ca_chain_path: str = "/secrets/swift/ca_chain.pem"
    connector_swift_username: str | None = None
    connector_swift_password: str | None = None

    # AML/KYC
    aml_threshold_usd: float = 10000.0

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    return Settings()