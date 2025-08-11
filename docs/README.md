# OpenBank Transfers Platform

Cloud-native open-source platform to initiate, track, and manage bank transfers (SWIFT & IBAN), with focus on DRC corridors. Backend uses FastAPI; frontend is React PWA. Infra provided for GCP (Cloud Run/GKE) and local dev via Docker Compose.

## Quickstart (dev)

- Prerequisites: Docker, Docker Compose, Node 20, Python 3.11 (optional for local tests)
- Start stack:

```bash
docker compose -f infra/docker-compose.yml up --build
```

- Backend: http://localhost:8080
- Frontend: http://localhost:5173
- Keycloak: http://localhost:8081
- Vault: http://localhost:8200
- Postgres: localhost:5432

## Backend local tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Production deploy

- Build and push images, deploy via Helm or Cloud Run manifests in `infra/`.

## Security notes

- No real transfers without bank credentials, client/server certificates, and written bank approval.
- Secrets must be in Vault or Google Secret Manager. Do not commit secrets.
- Dry-run mode is available to validate messages/connectivity without sending payments.