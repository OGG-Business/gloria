FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY backend/pyproject.toml /app/
RUN pip install --no-cache-dir -U pip setuptools wheel && pip install --no-cache-dir -e .

COPY backend/app /app/app
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini

EXPOSE 8443
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile", "/certs/dev-key.pem", "--ssl-certfile", "/certs/dev-cert.pem"]