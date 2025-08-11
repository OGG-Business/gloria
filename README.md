# Open Payments Hub (SWIFT/ISO 20022/Mojaloop)

Production-ready, cloud-native hub to initiate, track, and manage bank transfers (IBAN/BIC) with ISO 20022 `pacs.008` support, Mojaloop corridors, and pluggable SWIFT adapters. Includes FastAPI backend, React PWA frontend, PostgreSQL (Cloud SQL-ready), Flyway migrations, Docker/Helm, Prometheus/Grafana, and CI hooks.

## Quick start (dev)

- Prereqs: Docker, Docker Compose
- Start: `docker-compose up --build`
- Backend: http://localhost:8000/health
- Frontend: http://localhost:5173

## Services
- Auth: OIDC via Google or Keycloak (dev mode disables auth)
- Accounts: Manage IBAN/BIC accounts
- Transfers: Create and track transfers with events and SSE
- Connectors: SWIFT (REST/mTLS stub), Mojaloop
- KYC: Encrypted document storage (AES-256-GCM via Vault/GSM/env)
- Audit: Append-only logs with trace id
- Observability: Prometheus + Grafana

## Endpoints
- /auth, /accounts, /transfers, /transfers/{id}/events, /kyc, /admin, /hooks

## Security & Compliance
- OAuth2/OIDC with MFA for admins (via IdP)
- TLS 1.3 (Cloud run/GKE ingress), certs via Certificate Manager
- KYC/AML: auto-block > 10k USD (configurable), sanctions screening hooks
- Secrets: Vault or Google Secret Manager (never commit secrets)
- Dry-run mode prevents real payments during tests

## ISO 20022
- Minimal `pacs.008` builder under `backend/app/iso20022/`
- Mapping to MT variants is stubbed; extend parsers/serializers as needed

## Deploy
- Cloud Run: Build backend and frontend images; deploy with env vars and GSM/Vault
- GKE: Use Helm chart in `helm/`

## Constraints
- No real transfers without bank credentials, certificates, and written approval
- Secrets must be in Vault/GSM; `.env` only for local dev
- Dry-run default true

See `ONBOARDING_SWIFT.md` and `SECURITY_CHECKLIST.md`.
