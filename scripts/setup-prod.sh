#!/bin/bash

# SwiftPay Production Setup Script
# This script helps deploy SwiftPay to production environments
# WARNING: This script handles production deployment - review all settings carefully

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${NAMESPACE:-swiftpay}
ENVIRONMENT=${ENVIRONMENT:-production}
DOMAIN=${DOMAIN:-swiftpay.example.com}
VAULT_NAMESPACE=${VAULT_NAMESPACE:-vault}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking production deployment prerequisites..."
    
    # Check required tools
    local tools=("kubectl" "helm" "docker" "openssl" "curl" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        error "kubectl is not connected to a Kubernetes cluster"
    fi
    
    # Check Helm
    if ! helm version &> /dev/null; then
        error "Helm is not properly installed or configured"
    fi
    
    success "All prerequisites met"
}

# Create namespace
create_namespace() {
    log "Creating Kubernetes namespace: $NAMESPACE"
    
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace "$NAMESPACE" name="$NAMESPACE" --overwrite
    
    success "Namespace $NAMESPACE created/updated"
}

# Setup secrets
setup_secrets() {
    log "Setting up production secrets..."
    
    # Check if secrets exist
    if kubectl get secret swiftpay-secrets -n "$NAMESPACE" &> /dev/null; then
        warn "Secrets already exist. Skipping secret creation."
        return
    fi
    
    # Create secret template
    cat << EOF > /tmp/swiftpay-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: swiftpay-secrets
  namespace: $NAMESPACE
type: Opaque
stringData:
  # Database
  SPRING_DATASOURCE_PASSWORD: "REPLACE_WITH_ACTUAL_DB_PASSWORD"
  
  # Redis
  SPRING_DATA_REDIS_PASSWORD: "REPLACE_WITH_ACTUAL_REDIS_PASSWORD"
  
  # Vault
  VAULT_TOKEN: "REPLACE_WITH_ACTUAL_VAULT_TOKEN"
  
  # Encryption
  SWIFTPAY_SECURITY_ENCRYPTION_KEY: "REPLACE_WITH_32_BYTE_BASE64_KEY"
  
  # JWT
  SWIFTPAY_SECURITY_JWT_SECRET: "REPLACE_WITH_ACTUAL_JWT_SECRET"
  
  # SWIFT
  SWIFTPAY_SWIFT_USERNAME: "REPLACE_WITH_SWIFT_USERNAME"
  SWIFTPAY_SWIFT_PASSWORD: "REPLACE_WITH_SWIFT_PASSWORD"
  SWIFTPAY_SWIFT_CLIENT_CERT_PASSWORD: "REPLACE_WITH_CERT_PASSWORD"
  
  # Mojaloop
  SWIFTPAY_MOJALOOP_API_KEY: "REPLACE_WITH_MOJALOOP_API_KEY"
  
  # KYC/AML
  SWIFTPAY_KYC_API_KEY: "REPLACE_WITH_KYC_API_KEY"
  SWIFTPAY_SANCTIONS_API_KEY: "REPLACE_WITH_SANCTIONS_API_KEY"
  
  # Notifications
  SWIFTPAY_NOTIFICATIONS_EMAIL_PASSWORD: "REPLACE_WITH_EMAIL_PASSWORD"
  SWIFTPAY_NOTIFICATIONS_SMS_API_KEY: "REPLACE_WITH_SMS_API_KEY"
EOF
    
    warn "Secret template created at /tmp/swiftpay-secrets.yaml"
    warn "CRITICAL: You must edit this file and replace all placeholder values with actual secrets"
    warn "Then apply it with: kubectl apply -f /tmp/swiftpay-secrets.yaml"
    
    read -p "Press Enter after you have updated the secrets file and applied it..."
}

# Setup TLS certificates
setup_tls() {
    log "Setting up TLS certificates..."
    
    # Check if TLS secret exists
    if kubectl get secret swiftpay-tls -n "$NAMESPACE" &> /dev/null; then
        warn "TLS certificates already exist. Skipping TLS setup."
        return
    fi
    
    # Create certificate directories
    mkdir -p /tmp/swiftpay-certs
    
    # Generate production TLS certificate (self-signed for demo - use real certs in production)
    openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
        -keyout /tmp/swiftpay-certs/tls.key \
        -out /tmp/swiftpay-certs/tls.crt \
        -subj "/C=CD/ST=Kinshasa/L=Kinshasa/O=SwiftPay/CN=$DOMAIN" \
        -addext "subjectAltName=DNS:$DOMAIN,DNS:api.$DOMAIN,DNS:app.$DOMAIN"
    
    # Create TLS secret
    kubectl create secret tls swiftpay-tls \
        --cert=/tmp/swiftpay-certs/tls.crt \
        --key=/tmp/swiftpay-certs/tls.key \
        -n "$NAMESPACE"
    
    # Setup SWIFT mutual TLS certificates (placeholders)
    kubectl create secret generic swiftpay-swift-certs \
        --from-literal=client.p12="PLACEHOLDER_BASE64_ENCODED_CLIENT_CERT" \
        --from-literal=client-password="PLACEHOLDER_CLIENT_CERT_PASSWORD" \
        --from-literal=ca-trust.jks="PLACEHOLDER_BASE64_ENCODED_CA_TRUSTSTORE" \
        --from-literal=ca-password="PLACEHOLDER_CA_TRUSTSTORE_PASSWORD" \
        -n "$NAMESPACE" --dry-run=client -o yaml > /tmp/swift-certs-secret.yaml
    
    warn "SWIFT certificate secret template created at /tmp/swift-certs-secret.yaml"
    warn "You must replace placeholder values with actual base64-encoded certificates"
    
    # Clean up temporary files
    rm -rf /tmp/swiftpay-certs
    
    success "TLS certificates configured"
}

# Deploy infrastructure components
deploy_infrastructure() {
    log "Deploying infrastructure components..."
    
    # PostgreSQL
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    helm upgrade --install postgresql bitnami/postgresql \
        --namespace "$NAMESPACE" \
        --set auth.postgresPassword="$(kubectl get secret swiftpay-secrets -n $NAMESPACE -o jsonpath='{.data.SPRING_DATASOURCE_PASSWORD}' | base64 -d)" \
        --set auth.database=swiftpay \
        --set primary.persistence.size=50Gi \
        --set primary.resources.requests.memory=2Gi \
        --set primary.resources.requests.cpu=1000m \
        --set metrics.enabled=true \
        --set metrics.serviceMonitor.enabled=true
    
    # Redis
    helm upgrade --install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set auth.password="$(kubectl get secret swiftpay-secrets -n $NAMESPACE -o jsonpath='{.data.SPRING_DATA_REDIS_PASSWORD}' | base64 -d)" \
        --set master.persistence.size=10Gi \
        --set replica.replicaCount=1 \
        --set metrics.enabled=true \
        --set metrics.serviceMonitor.enabled=true
    
    # Vault (if not already deployed)
    if ! helm list -n "$VAULT_NAMESPACE" | grep -q vault; then
        helm repo add hashicorp https://helm.releases.hashicorp.com
        helm repo update
        
        kubectl create namespace "$VAULT_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        
        helm upgrade --install vault hashicorp/vault \
            --namespace "$VAULT_NAMESPACE" \
            --set server.ha.enabled=true \
            --set server.ha.replicas=3 \
            --set ui.enabled=true \
            --set ui.serviceType=ClusterIP
    fi
    
    success "Infrastructure components deployed"
}

# Deploy monitoring stack
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    # Prometheus & Grafana
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set grafana.adminPassword="$(openssl rand -base64 32)" \
        --set grafana.persistence.enabled=true \
        --set grafana.persistence.size=10Gi \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
    
    # ELK Stack
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Elasticsearch
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace logging \
        --create-namespace \
        --set replicas=3 \
        --set volumeClaimTemplate.resources.requests.storage=30Gi \
        --set esJavaOpts="-Xmx2g -Xms2g"
    
    # Kibana
    helm upgrade --install kibana elastic/kibana \
        --namespace logging \
        --set service.type=ClusterIP
    
    # Logstash
    helm upgrade --install logstash elastic/logstash \
        --namespace logging \
        --set replicas=2 \
        --set volumeClaimTemplate.resources.requests.storage=10Gi
    
    success "Monitoring stack deployed"
}

# Deploy SwiftPay application
deploy_application() {
    log "Deploying SwiftPay application..."
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/ -n "$NAMESPACE"
    
    # Deploy with Helm if chart exists
    if [ -d "helm/swiftpay" ]; then
        helm upgrade --install swiftpay ./helm/swiftpay \
            --namespace "$NAMESPACE" \
            --set image.tag="${IMAGE_TAG:-latest}" \
            --set ingress.hosts[0].host="$DOMAIN" \
            --set ingress.tls[0].secretName=swiftpay-tls \
            --set ingress.tls[0].hosts[0]="$DOMAIN"
    fi
    
    success "SwiftPay application deployed"
}

# Wait for deployments
wait_for_deployments() {
    log "Waiting for deployments to be ready..."
    
    # Wait for infrastructure
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n "$NAMESPACE" --timeout=300s
    
    # Wait for application
    kubectl wait --for=condition=ready pod -l app=swiftpay-backend -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=swiftpay-frontend -n "$NAMESPACE" --timeout=300s
    
    success "All deployments are ready"
}

# Run health checks
run_health_checks() {
    log "Running production health checks..."
    
    # Get service URLs
    local backend_url="https://api.$DOMAIN"
    local frontend_url="https://$DOMAIN"
    
    # Check backend health
    if curl -f -s "$backend_url/actuator/health" > /dev/null; then
        success "Backend health check passed"
    else
        error "Backend health check failed"
    fi
    
    # Check frontend
    if curl -f -s "$frontend_url" > /dev/null; then
        success "Frontend health check passed"
    else
        error "Frontend health check failed"
    fi
    
    # Check database connectivity
    kubectl exec -n "$NAMESPACE" deployment/swiftpay-backend -- \
        curl -f http://localhost:8081/actuator/health/db || error "Database connectivity check failed"
    
    # Check Redis connectivity
    kubectl exec -n "$NAMESPACE" deployment/swiftpay-backend -- \
        curl -f http://localhost:8081/actuator/health/redis || error "Redis connectivity check failed"
    
    success "All health checks passed"
}

# Setup monitoring alerts
setup_alerts() {
    log "Setting up production alerts..."
    
    # Create PrometheusRule for SwiftPay alerts
    cat << EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: swiftpay-alerts
  namespace: $NAMESPACE
  labels:
    app: swiftpay
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
  - name: swiftpay.rules
    rules:
    - alert: SwiftPayBackendDown
      expr: up{job="swiftpay-backend"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "SwiftPay Backend is down"
        description: "SwiftPay Backend has been down for more than 2 minutes."
    
    - alert: SwiftPayHighErrorRate
      expr: rate(http_requests_total{job="swiftpay-backend",status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High error rate detected"
        description: "SwiftPay is experiencing a high error rate ({{ \$value }} errors/sec)."
    
    - alert: SwiftPayDatabaseConnectionHigh
      expr: hikaricp_connections_active{job="swiftpay-backend"} > 80
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High database connection usage"
        description: "Database connection pool usage is high ({{ \$value }} active connections)."
    
    - alert: SwiftPayTransferProcessingDelay
      expr: increase(swiftpay_transfer_processing_duration_seconds_sum[10m]) / increase(swiftpay_transfer_processing_duration_seconds_count[10m]) > 30
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Transfer processing delays detected"
        description: "Average transfer processing time is {{ \$value }} seconds."
    
    - alert: SwiftPayVaultUnreachable
      expr: up{job="vault"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "HashiCorp Vault is unreachable"
        description: "Vault has been unreachable for more than 1 minute. Secrets access may be impacted."
EOF
    
    success "Production alerts configured"
}

# Backup procedures
setup_backup() {
    log "Setting up backup procedures..."
    
    # Create backup CronJob
    cat << EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: swiftpay-db-backup
  namespace: $NAMESPACE
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15-alpine
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: swiftpay-secrets
                  key: SPRING_DATASOURCE_PASSWORD
            command:
            - /bin/sh
            - -c
            - |
              TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
              pg_dump -h postgresql -U postgres -d swiftpay > /backup/swiftpay_backup_\$TIMESTAMP.sql
              # Keep only last 7 days of backups
              find /backup -name "swiftpay_backup_*.sql" -mtime +7 -delete
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: swiftpay-backup-pvc
          restartPolicy: OnFailure
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: swiftpay-backup-pvc
  namespace: $NAMESPACE
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
EOF
    
    success "Backup procedures configured"
}

# Security hardening
security_hardening() {
    log "Applying security hardening..."
    
    # Network policies
    cat << EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: swiftpay-network-policy
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: swiftpay-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: swiftpay-frontend
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector:
        matchLabels:
          name: $VAULT_NAMESPACE
    ports:
    - protocol: TCP
      port: 8200
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS outbound for SWIFT/Mojaloop
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
EOF
    
    # Pod Security Standards
    kubectl label namespace "$NAMESPACE" \
        pod-security.kubernetes.io/enforce=restricted \
        pod-security.kubernetes.io/audit=restricted \
        pod-security.kubernetes.io/warn=restricted
    
    success "Security hardening applied"
}

# Validate deployment
validate_deployment() {
    log "Validating production deployment..."
    
    # Check all pods are running
    local failed_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running --no-headers | wc -l)
    if [ "$failed_pods" -gt 0 ]; then
        error "Some pods are not running. Check with: kubectl get pods -n $NAMESPACE"
    fi
    
    # Check services are accessible
    local services=("swiftpay-backend" "swiftpay-frontend")
    for service in "${services[@]}"; do
        if ! kubectl get service "$service" -n "$NAMESPACE" &> /dev/null; then
            error "Service $service not found"
        fi
    done
    
    # Validate certificates
    log "Validating TLS certificates..."
    if ! kubectl get secret swiftpay-tls -n "$NAMESPACE" &> /dev/null; then
        error "TLS certificates not found"
    fi
    
    # Check monitoring
    if kubectl get servicemonitor -n "$NAMESPACE" swiftpay-backend &> /dev/null; then
        success "Monitoring integration active"
    else
        warn "Monitoring integration not detected"
    fi
    
    success "Deployment validation completed"
}

# Post-deployment tasks
post_deployment() {
    log "Executing post-deployment tasks..."
    
    # Get access information
    local backend_url="https://api.$DOMAIN"
    local frontend_url="https://$DOMAIN"
    local grafana_password=$(kubectl get secret -n monitoring kube-prometheus-stack-grafana -o jsonpath='{.data.admin-password}' | base64 -d)
    
    # Print access information
    cat << EOF

=============================================================================
                        SwiftPay Production Deployment Complete
=============================================================================

Access URLs:
  Frontend:     $frontend_url
  Backend API:  $backend_url
  API Docs:     $backend_url/swagger-ui/index.html
  Actuator:     $backend_url/actuator
  
Monitoring:
  Grafana:      http://grafana.$DOMAIN (admin / $grafana_password)
  Prometheus:   http://prometheus.$DOMAIN
  Kibana:       http://kibana.$DOMAIN
  
Administrative:
  Namespace:    $NAMESPACE
  Environment:  $ENVIRONMENT
  
Next Steps:
  1. Configure DNS records for $DOMAIN
  2. Update secrets with real values (see /tmp/swiftpay-secrets.yaml)
  3. Replace TLS certificates with production certificates
  4. Configure SWIFT certificates (see /tmp/swift-certs-secret.yaml)
  5. Review and test all endpoints
  6. Configure external monitoring and alerting
  7. Setup log aggregation and retention policies
  8. Review security policies and access controls

CRITICAL REMINDERS:
  - Review all secrets and certificates before processing real transfers
  - Ensure bank agreements and compliance requirements are met
  - Test connectivity with bank partners in sandbox mode first
  - Monitor logs and metrics continuously
  - Maintain regular backups and disaster recovery procedures

=============================================================================
EOF
    
    success "Post-deployment tasks completed"
}

# Main execution
main() {
    log "Starting SwiftPay production deployment..."
    
    # Confirmation
    warn "This script will deploy SwiftPay to production environment: $ENVIRONMENT"
    warn "Namespace: $NAMESPACE, Domain: $DOMAIN"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log "Deployment cancelled by user"
        exit 0
    fi
    
    check_prerequisites
    create_namespace
    setup_secrets
    setup_tls
    deploy_infrastructure
    deploy_monitoring
    setup_alerts
    setup_backup
    security_hardening
    deploy_application
    wait_for_deployments
    run_health_checks
    validate_deployment
    post_deployment
    
    success "SwiftPay production deployment completed successfully!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi