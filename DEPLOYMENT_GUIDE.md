# SwiftPay Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying SwiftPay in different environments.

## Prerequisites

### Development Environment
- Docker & Docker Compose
- Java 17+ (for local development)
- Node.js 18+ (for frontend development)
- Git

### Production Environment
- Kubernetes cluster (1.24+)
- Helm 3.12+
- kubectl configured
- HashiCorp Vault
- PostgreSQL 15+ (managed service recommended)
- Redis 7+ (managed service recommended)
- Certificate management solution

## Quick Start (Development)

### 1. Clone and Setup
```bash
git clone https://github.com/swiftpay/swiftpay.git
cd swiftpay
./scripts/setup-dev.sh
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Verify Installation
```bash
./scripts/test-integration.sh
```

### 4. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui/index.html
- **Grafana**: http://localhost:3001 (admin/admin)
- **Kibana**: http://localhost:5601

## Production Deployment

### Phase 1: Infrastructure Preparation

#### 1. Kubernetes Cluster Setup
```bash
# Create namespaces
kubectl apply -f k8s/manifests/namespace.yaml

# Apply security policies
./scripts/security-hardening.sh
```

#### 2. External Services Setup

**PostgreSQL Database:**
- Create managed PostgreSQL instance
- Configure connection pooling
- Set up automated backups
- Configure monitoring

**Redis Cache:**
- Create managed Redis instance
- Configure persistence
- Set up monitoring

**HashiCorp Vault:**
- Deploy Vault cluster
- Configure authentication
- Set up secret engines
- Configure policies

#### 3. Certificate Management
```bash
# Install production certificates
cp /path/to/certificates/* certs/production/
chmod 600 certs/production/*/*

# Verify certificates
openssl pkcs12 -info -in certs/production/swift/swift-client.p12 -noout
keytool -list -keystore certs/production/swift/swift-ca.jks
```

### Phase 2: Configuration

#### 1. Environment Configuration
```bash
# Copy and configure production environment
cp .env.example .env.production
# Edit .env.production with production values
```

#### 2. Kubernetes Secrets
```bash
# Update secrets with production values
vim config/production/secrets.yaml

# Apply secrets
kubectl apply -f config/production/secrets.yaml
```

#### 3. Monitoring Setup
```bash
# Install monitoring stack
./scripts/setup-monitoring.sh
```

### Phase 3: Application Deployment

#### 1. Build and Push Images
```bash
# Build images
docker build -t ghcr.io/swiftpay/backend:v1.0.0 ./backend/
docker build -t ghcr.io/swiftpay/frontend:v1.0.0 ./frontend/

# Push to registry
docker push ghcr.io/swiftpay/backend:v1.0.0
docker push ghcr.io/swiftpay/frontend:v1.0.0
```

#### 2. Deploy with Helm
```bash
# Deploy to production
helm upgrade --install swiftpay ./helm/swiftpay \
  --namespace swiftpay-prod \
  --values ./helm/swiftpay/values/production.yaml \
  --set image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0 \
  --wait \
  --timeout=15m
```

#### 3. Post-Deployment Verification
```bash
# Run health checks
./scripts/health-check-prod.sh

# Verify all services
kubectl get pods -n swiftpay-prod
kubectl get services -n swiftpay-prod
kubectl get ingress -n swiftpay-prod
```

## Banking Integration

### SWIFT Integration

**Prerequisites:**
- SWIFT membership and BIC code
- Bank partnership agreements
- Production certificates from bank
- Network connectivity setup

**Steps:**
1. Follow `ONBOARDING_SWIFT.md` for detailed instructions
2. Install production certificates
3. Configure SWIFT endpoints in `.env.production`
4. Test connectivity in dry-run mode
5. Coordinate with bank for production testing

### Mojaloop Integration

**Prerequisites:**
- Mojaloop participant registration
- API credentials
- Network setup

**Steps:**
1. Register as Mojaloop participant
2. Obtain API credentials
3. Configure endpoints in `.env.production`
4. Test with sandbox environment
5. Move to production after validation

## Security Checklist

### Pre-Production Security Review

- [ ] All secrets managed via Vault
- [ ] TLS 1.3 enforced everywhere
- [ ] Database encrypted at rest and in transit
- [ ] API rate limiting configured
- [ ] Input validation comprehensive
- [ ] Authentication/authorization tested
- [ ] Audit logging enabled
- [ ] Security scanning completed
- [ ] Penetration testing performed

### Production Security Monitoring

- [ ] Security event alerting configured
- [ ] Failed login attempt monitoring
- [ ] Suspicious transaction detection
- [ ] Certificate expiry monitoring
- [ ] Vulnerability scanning scheduled
- [ ] Incident response procedures ready

## Monitoring and Observability

### Metrics to Monitor

**Application Metrics:**
- Transfer success/failure rates
- API response times
- Error rates by endpoint
- Authentication failures

**Infrastructure Metrics:**
- CPU and memory usage
- Database performance
- Network connectivity
- Certificate expiry dates

**Business Metrics:**
- Transaction volumes
- Revenue metrics
- Geographic distribution
- Customer satisfaction

### Alerting Rules

**Critical Alerts:**
- Transfer failure rate > 5%
- API response time > 2s
- Database connectivity loss
- SWIFT connectivity loss
- Security breaches

**Warning Alerts:**
- High resource usage
- Certificate expiry < 30 days
- Unusual transaction patterns
- Performance degradation

## Backup and Recovery

### Backup Strategy

**Database Backups:**
- Daily full backups
- Hourly incremental backups
- Cross-region replication
- 7-year retention for financial data

**Configuration Backups:**
- Kubernetes manifests
- Helm values
- Certificates (encrypted)
- Environment configurations

### Disaster Recovery

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 1 hour

**Recovery Procedures:**
1. Activate disaster recovery site
2. Restore database from latest backup
3. Deploy application with Helm
4. Verify all integrations
5. Switch DNS to recovery site

## Scaling and Performance

### Horizontal Scaling

**Auto-scaling Configuration:**
- CPU threshold: 70%
- Memory threshold: 80%
- Min replicas: 3 (production)
- Max replicas: 10

### Performance Optimization

**Database Optimization:**
- Connection pooling
- Read replicas for reporting
- Query optimization
- Index maintenance

**Application Optimization:**
- JVM tuning
- Connection pooling
- Caching strategies
- Async processing

## Compliance and Auditing

### Regulatory Compliance

**Know Your Customer (KYC):**
- Identity verification
- Document collection
- Risk assessment
- Ongoing monitoring

**Anti-Money Laundering (AML):**
- Transaction monitoring
- Sanctions screening
- Suspicious activity reporting
- Record keeping

### Audit Requirements

**Audit Logs:**
- All API requests
- Authentication events
- Configuration changes
- Administrative actions

**Retention Policies:**
- Transaction data: 7 years
- Audit logs: 7 years
- Security logs: 1 year
- Application logs: 90 days

## Troubleshooting

### Common Issues

**Service Won't Start:**
1. Check pod logs: `kubectl logs -f deployment/swiftpay-backend -n swiftpay-prod`
2. Verify secrets are properly configured
3. Check database connectivity
4. Verify certificate validity

**SWIFT Connectivity Issues:**
1. Test certificate validity
2. Check network connectivity
3. Verify BIC configuration
4. Review SWIFT endpoint settings

**Performance Issues:**
1. Check resource utilization
2. Review database performance
3. Analyze application metrics
4. Check network latency

### Support Contacts

**Technical Support:**
- Email: support@swiftpay.local
- Slack: #swiftpay-support
- On-call: +1-XXX-XXX-XXXX

**Banking Integration:**
- SWIFT Support: swift-support@bank.local
- Mojaloop Support: support@mojaloop.io

## Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review security alerts
- Check system performance
- Verify backup integrity
- Update security patches

**Monthly:**
- Certificate expiry review
- Performance optimization
- Capacity planning
- Security assessment

**Quarterly:**
- Disaster recovery testing
- Security penetration testing
- Compliance review
- Business continuity testing

## Version Management

### Release Process

1. **Development**: Feature development on `develop` branch
2. **Testing**: Automated testing via GitHub Actions
3. **Staging**: Deploy to staging environment for integration testing
4. **Production**: Deploy via GitHub release with proper tagging

### Rollback Procedures

```bash
# Rollback to previous version
helm rollback swiftpay -n swiftpay-prod

# Verify rollback
./scripts/health-check-prod.sh
```

---

**Important**: This deployment guide should be reviewed and updated regularly to reflect changes in infrastructure, security requirements, and regulatory compliance.