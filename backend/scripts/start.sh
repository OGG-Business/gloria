#!/bin/bash

# Script de démarrage pour Banking Transfer Platform Backend

set -e

echo "Starting Banking Transfer Platform Backend..."

# Vérifier les variables d'environnement critiques
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY is not set"
    exit 1
fi

if [ -z "$ENCRYPTION_KEY" ]; then
    echo "ERROR: ENCRYPTION_KEY is not set"
    exit 1
fi

# Attendre que la base de données soit prête
echo "Waiting for database to be ready..."
python -c "
import time
import psycopg2
import os

max_retries = 30
retry_interval = 2

for i in range(max_retries):
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.close()
        print('Database is ready!')
        exit(0)
    except Exception as e:
        print(f'Database not ready yet (attempt {i+1}/{max_retries}): {e}')
        if i < max_retries - 1:
            time.sleep(retry_interval)
        else:
            print('Database connection failed after maximum retries')
            exit(1)
"

# Exécuter les migrations si nécessaire
echo "Running database migrations..."
python -m alembic upgrade head

# Vérifier la santé de l'application
echo "Checking application health..."
python -c "
import requests
import time
import sys

max_retries = 10
retry_interval = 2

for i in range(max_retries):
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print('Application is healthy!')
            sys.exit(0)
        else:
            print(f'Health check failed with status {response.status_code}')
    except Exception as e:
        print(f'Health check failed (attempt {i+1}/{max_retries}): {e}')
    
    if i < max_retries - 1:
        time.sleep(retry_interval)

print('Application health check failed after maximum retries')
sys.exit(1)
" || echo "Health check skipped (application not running yet)"

# Démarrer l'application
echo "Starting FastAPI application..."
exec uvicorn app.main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips="*"