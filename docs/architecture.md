# Architecture (Google Cloud)

```mermaid
flowchart LR
  subgraph Client
    Web[React PWA]
  end

  subgraph GCP[Google Cloud]
    CR[Cloud Run - Backend]
    FH[Firebase Hosting/Cloud Run - Frontend]
    SQL[(Cloud SQL - PostgreSQL)]
    GSM[Secret Manager]
    VAULT[HashiCorp Vault]
    PS[Pub/Sub]
    MON[Cloud Monitoring]
    LOG[Cloud Logging]
    CEP[Cloud Endpoints]
    GKE[GKE (Helm - optional)]
  end

  Bank[Bank SWIFT/Mojaloop]

  Web --> FH --> CR
  CR <--> SQL
  CR <--> GSM
  CR <--> VAULT
  CR --> PS
  PS --> CR
  CR --> MON
  CR --> LOG
  FH --> MON
  CR -.-> CEP

  CR -->|SWIFT REST mTLS / SFTP / AS4| Bank
  CR -->|Mojaloop| Bank
```

- Auth: OIDC via Google Identity Platform or Keycloak
- Accounts: Accounts service within the FastAPI app (modular monolith)
- Transfers: State machine with events, `pacs.008` builder, connectors
- Connectors: SWIFT (REST/mTLS, SFTP, AS4), Mojaloop
- KYC: Encrypted documents via AES-256-GCM with keys from Vault/GSM
- Notifications: SSE to clients; optional Pub/Sub bridge
- Audit: Append-only DB table with `X-Trace-ID`
- Observability: Prometheus metrics + Cloud Monitoring; structured logs

Deployment:
- Serverless (Cloud Run) for backend and frontend
- Or Kubernetes (GKE) with Helm chart in `helm/`

OpenAPI:
- `openapi.yaml` served by Cloud Endpoints with ESPv2 in front of Cloud Run