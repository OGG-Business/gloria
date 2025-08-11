#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=${PROJECT_ID:?}
REGION=${REGION:-europe-west1}
SERVICE=${SERVICE:-gpp-backend}
DB_INSTANCE=${DB_INSTANCE:-gpp-postgres}
DB_USER=${DB_USER:-app}
DB_PASSWORD=${DB_PASSWORD:?}
DB_NAME=${DB_NAME:-app}
BUCKET=${BUCKET:-gpp-frontend-$PROJECT_ID}

# Enable required services
gcloud services enable run.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com compute.googleapis.com --project $PROJECT_ID

# Create Cloud SQL Postgres 15
if ! gcloud sql instances describe $DB_INSTANCE --project $PROJECT_ID >/dev/null 2>&1; then
  gcloud sql instances create $DB_INSTANCE --database-version=POSTGRES_15 --cpu=2 --memory=7680MB --region=$REGION --project $PROJECT_ID
fi

# Create DB and user
if ! gcloud sql databases describe $DB_NAME --instance=$DB_INSTANCE --project $PROJECT_ID >/dev/null 2>&1; then
  gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE --project $PROJECT_ID
fi

gcloud sql users create $DB_USER --instance=$DB_INSTANCE --password=$DB_PASSWORD --project $PROJECT_ID || true

# Secret Manager
printf %s "$DB_PASSWORD" | gcloud secrets create DB_PASSWORD --replication-policy="automatic" --data-file=- --project $PROJECT_ID || true

# Bucket for frontend
gsutil mb -l $REGION gs://$BUCKET || true

echo "Provisioning complete"