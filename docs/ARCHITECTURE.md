# Architecture

## GCP Diagram (conceptual)

```mermaid
flowchart LR
  subgraph GCP
    subgraph CloudRun[Cloud Run]
      Backend[(FastAPI Backend)]
      Notifications[(SSE/WebSocket)]
    end
    subgraph CloudSQL[Cloud SQL]
      PG[(PostgreSQL)]
    end
    subgraph Security[Secrets]
      GSM[Google Secret Manager]
      Vault[HashiCorp Vault]
    end
    subgraph Observability
      CM[Cloud Monitoring/Prometheus]
      CL[Cloud Logging]
    end
    subgraph Endpoints[Cloud Endpoints]
      OpenAPI[(OpenAPI/Swagger)]
    end
    PubSub[(Pub/Sub)]
  end

  Users((Web/Mobile)) -->|HTTPS + OIDC| Backend
  Backend --> PG
  Backend --> PubSub
  Backend --> GSM
  Backend --> Vault
  Backend --> CM
  Backend --> CL
  OpenAPI --> Backend

  subgraph External
    SWIFT[(SWIFT Network)]
    Mojaloop[(Mojaloop DFSPs)]
  end

  Backend <--> SWIFT
  Backend <--> Mojaloop
```

## Services
- Auth Service: Keycloak or Google Identity Platform (OIDC/OAuth2)
- Accounts Service: account metadata, IBAN/BIC validation
- Transfers Service: state orchestration, pacs.008, MT mapping, events
- Connectors Service: SWIFT (AS4/SFTP/REST, mTLS), Mojaloop adapters
- KYC Service: encrypted document storage and screening hooks
- Notifications Service: Pub/Sub -> SSE/WebSocket streaming
- Audit Service: append-only logs with hash chaining
- Observability: Prometheus metrics, Cloud Logging, tracing

## Data
- PostgreSQL managed via Cloud SQL in prod; Flyway migrations in `db/migrations`.