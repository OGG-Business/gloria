#!/bin/bash

# SwiftPay Production Setup Script
# This script helps prepare the production environment for SwiftPay
# WARNING: This script should be run by authorized personnel only

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi

log "Starting SwiftPay Production Setup..."

# Check prerequisites
log "Checking prerequisites..."

# Check for required tools
for tool in kubectl helm docker openssl; do
    if ! command -v $tool &> /dev/null; then
        error "$tool is required but not installed"
    fi
done

# Check Kubernetes connection
if ! kubectl cluster-info &> /dev/null; then
    error "Cannot connect to Kubernetes cluster. Please check your kubeconfig"
fi

# Create production directories
log "Creating production directories..."
mkdir -p {certs/production,config/production,secrets,backups,logs}

# Production environment configuration
log "Setting up production environment variables..."

if [[ ! -f .env.production ]]; then
    cat > .env.production << 'EOF'
# SwiftPay Production Environment Configuration
# WARNING: Fill in all values before deployment

# Application
SPRING_PROFILES_ACTIVE=production
SERVER_PORT=8080
MANAGEMENT_SERVER_PORT=8081

# Database (Production PostgreSQL)
DB_HOST=swiftpay-postgres.database.svc.cluster.local
DB_PORT=5432
DB_NAME=swiftpay_prod
DB_USERNAME=swiftpay_user
DB_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# Redis (Production)
REDIS_HOST=swiftpay-redis.cache.svc.cluster.local
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_ME_REDIS_PASSWORD

# HashiCorp Vault (Production)
VAULT_URI=https://vault.swiftpay.local:8200
VAULT_TOKEN=CHANGE_ME_VAULT_TOKEN
VAULT_NAMESPACE=swiftpay
VAULT_MOUNT_PATH=secret

# Keycloak (Production)
KEYCLOAK_SERVER_URL=https://auth.swiftpay.local
KEYCLOAK_REALM=swiftpay-prod
KEYCLOAK_CLIENT_ID=swiftpay-backend
KEYCLOAK_CLIENT_SECRET=CHANGE_ME_KEYCLOAK_SECRET

# Encryption
ENCRYPTION_KEY=CHANGE_ME_32_CHAR_ENCRYPTION_KEY
ENCRYPTION_SALT=CHANGE_ME_16_CHAR_SALT

# SWIFT Configuration (PRODUCTION - HANDLE WITH EXTREME CARE)
SWIFT_ENABLED=true
SWIFT_ENDPOINT=https://swift.production.bank.local/api/v1
SWIFT_BIC=CHANGE_ME_YOUR_BIC
SWIFT_CLIENT_CERT_PATH=/app/certs/swift-client.p12
SWIFT_CLIENT_CERT_PASSWORD=CHANGE_ME_CERT_PASSWORD
SWIFT_CA_CERT_PATH=/app/certs/swift-ca.jks
SWIFT_CA_CERT_PASSWORD=CHANGE_ME_CA_PASSWORD
SWIFT_TIMEOUT_MS=30000
SWIFT_RETRY_ATTEMPTS=3

# Mojaloop (Production)
MOJALOOP_ENABLED=true
MOJALOOP_ENDPOINT=https://mojaloop.prod.local/api/v1
MOJALOOP_PARTICIPANT_ID=CHANGE_ME_PARTICIPANT_ID
MOJALOOP_API_KEY=CHANGE_ME_MOJALOOP_API_KEY

# KYC/AML
KYC_ENABLED=true
KYC_DOCUMENT_STORAGE_PATH=/app/data/kyc-documents
AML_SCREENING_ENABLED=true
AML_SANCTIONS_API_URL=https://sanctions-api.prod.local
AML_SANCTIONS_API_KEY=CHANGE_ME_SANCTIONS_API_KEY

# Notifications
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_SMTP_HOST=smtp.prod.local
NOTIFICATION_EMAIL_SMTP_PORT=587
NOTIFICATION_EMAIL_USERNAME=CHANGE_ME_EMAIL_USER
NOTIFICATION_EMAIL_PASSWORD=CHANGE_ME_EMAIL_PASSWORD
NOTIFICATION_SMS_ENABLED=true
NOTIFICATION_SMS_API_URL=https://sms-api.prod.local
NOTIFICATION_SMS_API_KEY=CHANGE_ME_SMS_API_KEY

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_ENDPOINT=http://prometheus.monitoring.svc.cluster.local:9090
GRAFANA_ENABLED=true
ELASTICSEARCH_HOSTS=elasticsearch.logging.svc.cluster.local:9200

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_REQUESTS_PER_HOUR=1000

# File Upload
FILE_UPLOAD_MAX_SIZE=10MB
FILE_UPLOAD_ALLOWED_TYPES=pdf,jpg,jpeg,png

# Webhooks
WEBHOOK_ENABLED=true
WEBHOOK_RETRY_ATTEMPTS=5
WEBHOOK_TIMEOUT_MS=10000

# Development/Testing (DISABLE IN PRODUCTION)
DEVELOPMENT_MODE=false
TEST_MODE=false
MOCK_SWIFT=false
MOCK_MOJALOOP=false
EOF

    warn "Created .env.production template. YOU MUST FILL IN ALL VALUES BEFORE DEPLOYMENT!"
else
    log ".env.production already exists, skipping creation"
fi

# Production certificate setup
log "Setting up production certificate directories..."

# Create certificate directories with proper permissions
mkdir -p certs/production/{swift,mojaloop,tls}
chmod 700 certs/production
chmod 700 certs/production/*

# Certificate installation instructions
cat > certs/production/CERTIFICATE_SETUP.md << 'EOF'
# Production Certificate Setup

## SWIFT Certificates

1. Obtain certificates from your bank/SWIFT partner:
   - Client certificate (PKCS12 format): `swift-client.p12`
   - CA certificate bundle (JKS format): `swift-ca.jks`
   - Certificate passwords

2. Install certificates:
   ```bash
   # Copy certificates to production directory
   cp /path/to/swift-client.p12 certs/production/swift/
   cp /path/to/swift-ca.jks certs/production/swift/
   
   # Set proper permissions
   chmod 600 certs/production/swift/*
   ```

3. Verify certificates:
   ```bash
   # Test client certificate
   openssl pkcs12 -info -in certs/production/swift/swift-client.p12 -noout
   
   # Test CA certificate
   keytool -list -keystore certs/production/swift/swift-ca.jks
   ```

## TLS Certificates

1. For production TLS, use certificates from a trusted CA
2. Install certificates:
   ```bash
   cp /path/to/swiftpay.crt certs/production/tls/
   cp /path/to/swiftpay.key certs/production/tls/
   cp /path/to/ca-bundle.crt certs/production/tls/
   chmod 600 certs/production/tls/*
   ```

## Certificate Rotation

Production certificates should be rotated regularly:
- SWIFT certificates: As per bank requirements (typically annually)
- TLS certificates: Every 90 days (recommended)

Use the provided rotation scripts in scripts/cert-rotation/
EOF

# Kubernetes namespace setup
log "Setting up Kubernetes namespace..."

kubectl create namespace swiftpay-prod --dry-run=client -o yaml | kubectl apply -f -

# Create Kubernetes secrets template
log "Creating Kubernetes secrets template..."

cat > config/production/secrets.yaml << 'EOF'
# Kubernetes Secrets for SwiftPay Production
# WARNING: Fill in all base64-encoded values before applying

apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-database
  namespace: swiftpay-prod
type: Opaque
data:
  username: c3dpZnRwYXlfdXNlcg==  # swiftpay_user (base64)
  password: Q0hBTkdFX01FX1NUUk9OR19QQVNTV09SRA==  # CHANGE_ME_STRONG_PASSWORD (base64)

---
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-redis
  namespace: swiftpay-prod
type: Opaque
data:
  password: Q0hBTkdFX01FX1JFRElTX1BBU1NXT1JE  # CHANGE_ME_REDIS_PASSWORD (base64)

---
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-encryption
  namespace: swiftpay-prod
type: Opaque
data:
  key: Q0hBTkdFX01FXzMyX0NIQVJfRU5DUllQVElPTl9LRVk=  # CHANGE_ME_32_CHAR_ENCRYPTION_KEY (base64)
  salt: Q0hBTkdFX01FXzE2X0NIQVJfU0FMVA==  # CHANGE_ME_16_CHAR_SALT (base64)

---
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-keycloak
  namespace: swiftpay-prod
type: Opaque
data:
  client-secret: Q0hBTkdFX01FX0tFWUNMT0FLX1NFQ1JFVA==  # CHANGE_ME_KEYCLOAK_SECRET (base64)

---
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-swift
  namespace: swiftpay-prod
type: Opaque
data:
  bic: Q0hBTkdFX01FX1lPVVJfQklD  # CHANGE_ME_YOUR_BIC (base64)
  cert-password: Q0hBTkdFX01FX0NFUlRfUEFTU1dPUkQ=  # CHANGE_ME_CERT_PASSWORD (base64)
  ca-password: Q0hBTkdFX01FX0NBX1BBU1NXT1JE  # CHANGE_ME_CA_PASSWORD (base64)

---
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-mojaloop
  namespace: swiftpay-prod
type: Opaque
data:
  participant-id: Q0hBTkdFX01FX1BBUlRJQ0lQQU5UX0lE  # CHANGE_ME_PARTICIPANT_ID (base64)
  api-key: Q0hBTkdFX01FX01PSkFMT09QX0FQSV9LRVk=  # CHANGE_ME_MOJALOOP_API_KEY (base64)

---
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-vault
  namespace: swiftpay-prod
type: Opaque
data:
  token: Q0hBTkdFX01FX1ZBVUxUX1RPS0VO  # CHANGE_ME_VAULT_TOKEN (base64)
EOF

log "Production setup completed successfully!"

echo
echo "Production Setup Summary"
echo "========================"
echo "✓ Production environment configuration created (.env.production)"
echo "✓ Kubernetes secrets template created (config/production/secrets.yaml)"
echo "✓ Certificate directories and setup instructions created"
echo "✓ Production namespace created in Kubernetes"
echo

warn "IMPORTANT NEXT STEPS:"
echo "1. Fill in all values in .env.production"
echo "2. Update base64-encoded secrets in config/production/secrets.yaml"
echo "3. Install production certificates in certs/production/"
echo "4. Run additional setup scripts as needed"
echo

warn "CRITICAL: Do not deploy to production without completing the full security review and obtaining all necessary banking agreements and certificates!"