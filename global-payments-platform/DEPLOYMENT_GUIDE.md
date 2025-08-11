# Deployment Guide (GCP)

## Prérequis
- Projet GCP, facturation activée
- gcloud SDK, droits Owner/Editor
- APIs: Cloud Run/App Engine, Cloud Build, Cloud SQL, Secret Manager, Cloud Storage, Compute, Identity Toolkit

## Provisionnement
```bash
export PROJECT_ID=your-project
export REGION=europe-west1
export DB_PASSWORD='strongpass'
./scripts/gcp/provision.sh
```
- Cloud SQL Postgres 15: instance+db+user
- Secret Manager: DB_PASSWORD
- GCS bucket: gpp-frontend-$PROJECT_ID

## Backend (Spring Boot) – Cloud Run
- Configurer substitutions dans `cloudbuild.yaml` (_REGION, _SERVICE)
- Déployer:
```bash
gcloud builds submit --config cloudbuild.yaml
```
- Variable d’env: `SPRING_PROFILES_ACTIVE=prod`
- Connexion Cloud SQL: définir `CLOUDSQL_INSTANCE` (format project:region:instance) et variables DB_USER/DB_PASSWORD via Secret Manager ou env.

## Backend – App Engine (option)
- Éditer `backend-spring/src/main/resources/app.yaml` (CLOUDSQL_INSTANCE, secrets)
- Déployer:
```bash
cd backend-spring
gcloud app deploy src/main/resources/app.yaml
```

## OAuth2 (Identity Platform)
- Activer Identity Platform
- Ajouter un fournisseur OIDC/Google selon besoin
- Backend: `application.yml` issuer `https://securetoken.google.com/YOUR_GCP_PROJECT_ID` (ou `https://accounts.google.com` en prod), frontend utilise les flux OAuth côté client pour obtenir un JWT à transmettre au backend.

## Frontend (React) – GCS + CDN
- Build:
```bash
cd frontend
npm ci && npm run build
```
- Déployer:
```bash
export BUCKET=gpp-frontend-$PROJECT_ID
gsutil -m rsync -r dist gs://$BUCKET
gsutil web set -m index.html -e index.html gs://$BUCKET
gsutil iam ch allUsers:objectViewer gs://$BUCKET
```
- Activer Cloud CDN sur un backend bucket (HTTPS load balancer) pour domaine custom.

## CI/CD (Cloud Build + GitHub)
- Créer Workload Identity Federation, secrets `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT` dans GitHub
- Le workflow `.github/workflows/gcp-deploy.yml` soumet Cloud Build sur push main

## Secrets
- Utiliser Secret Manager pour DB_PASSWORD, API Keys (ex: PSD2 AddAPIKey)
- Consommer les secrets via env (App Engine `sm://`), ou injection à l’exécution Cloud Run.

## CORS & HTTPS
- Toujours exposer via HTTPS
- Mettre à jour `application-prod.yml` `app.cors.allowed-origins` avec votre domaine frontend CDN

## Observabilité
- Actuator + Prometheus endpoint `/actuator/prometheus`
- Intégrer Cloud Monitoring/Logging selon besoins