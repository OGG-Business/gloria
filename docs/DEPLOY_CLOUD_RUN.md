# Deploy to Cloud Run and Cloud Endpoints

## Build and push image
```bash
gcloud builds submit --tag gcr.io/$PROJECT/openbank-backend:latest backend
```

## Create Cloud SQL instance and database
```bash
gcloud sql instances create transfers-sql --database-version=POSTGRES_16 --tier=db-f1-micro --region=$REGION
gcloud sql databases create transfers --instance=transfers-sql
gcloud sql users set-password postgres --instance=transfers-sql --password=YOUR_PASSWORD
```

## Deploy to Cloud Run
```bash
gcloud run deploy openbank-backend \
  --image gcr.io/$PROJECT/openbank-backend:latest \
  --region $REGION \
  --allow-unauthenticated \
  --add-cloudsql-instances $PROJECT:$REGION:transfers-sql \
  --set-env-vars APP_APP_ENV=prod,APP_AUTH_DISABLED=false,APP_USE_DB=true,APP_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/transfers,APP_DRY_RUN=true
```

## Configure Endpoints
```bash
gcloud endpoints services deploy infra/cloudendpoints/openapi-run.yaml
```