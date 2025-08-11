# Banking Transfer Platform

Plateforme cloud-native complète pour l'initiation, le suivi et la gestion de transferts bancaires internationaux (SWIFT & IBAN) avec support spécial pour les banques opérant en RDC.

## 🏗️ Architecture

### Services Microservices
- **Auth Service**: Authentification OAuth2/OpenID Connect (Keycloak)
- **Accounts Service**: Gestion des comptes bancaires
- **Transfers Service**: Orchestration des transferts
- **Connectors Service**: Connecteurs SWIFT et Mojaloop
- **KYC Service**: Conformité KYC/AML
- **Notifications Service**: Notifications temps réel
- **Audit Service**: Journalisation et audit
- **Observability**: Monitoring et logging

### Technologies
- **Backend**: FastAPI (Python) - Performance, async, validation automatique
- **Frontend**: React + TypeScript + PWA
- **Base de données**: PostgreSQL (Cloud SQL)
- **Containerisation**: Docker + Kubernetes
- **Cloud**: Google Cloud Platform
- **Sécurité**: HashiCorp Vault, TLS 1.3, MFA

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- kubectl (pour déploiement K8s)

### Développement Local
```bash
# Cloner le projet
git clone <repository-url>
cd banking-transfer-platform

# Démarrer tous les services
docker-compose up -d

# Vérifier les services
curl http://localhost:8000/health
curl http://localhost:3000

# Exécuter les tests
make test
make test-coverage
```

### Déploiement Production
```bash
# Build et push des images
make build-images
make push-images

# Déploiement Kubernetes
helm install banking-platform ./helm/
```

## 📋 Fonctionnalités

### Transferts Bancaires
- ✅ Initiation de transferts SWIFT/IBAN
- ✅ Validation automatique IBAN/BIC
- ✅ Suivi en temps réel des statuts
- ✅ Support ISO 20022 (pacs.008)
- ✅ Mapping MT messages
- ✅ Connecteurs Mojaloop (Afrique)

### Sécurité & Conformité
- ✅ OAuth2/OpenID Connect
- ✅ Chiffrement AES-256
- ✅ MFA pour admins
- ✅ KYC/AML automatisé
- ✅ Audit trail complet
- ✅ Screening sanctions

### Interface Utilisateur
- ✅ Dashboard responsive
- ✅ PWA (offline-first)
- ✅ Notifications temps réel
- ✅ Interface admin complète
- ✅ Support mobile/tablette

## 🔧 Configuration

### Variables d'Environnement
```bash
# Base de données
DATABASE_URL=postgresql://user:pass@host:5432/banking

# Sécurité
VAULT_ADDR=https://vault.example.com
VAULT_TOKEN=your-token

# SWIFT
SWIFT_BIC=YOURBIC
SWIFT_CERT_PATH=/path/to/cert.pem
SWIFT_KEY_PATH=/path/to/key.pem

# Mojaloop
MOJALOOP_ENDPOINT=https://mojaloop.example.com
```

### Certificats SWIFT
1. Obtenir certificats X.509 de votre banque
2. Configurer TLS mutual authentication
3. Tester la connectivité
4. Voir `docs/ONBOARDING_SWIFT.md`

## 📊 Monitoring

### Métriques
- Prometheus + Grafana
- Cloud Monitoring (GCP)
- Alertes automatiques

### Logs
- Cloud Logging (GCP)
- Corrélation par trace ID
- Audit trail complet

## 🧪 Tests

```bash
# Tests unitaires
pytest backend/tests/unit/

# Tests d'intégration
pytest backend/tests/integration/

# Tests E2E
npm run test:e2e

# Couverture
make coverage-report
```

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [SWIFT Onboarding](docs/ONBOARDING_SWIFT.md)
- [Security Checklist](docs/SECURITY.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🔒 Sécurité

### Checklist Production
- [ ] Certificats TLS configurés
- [ ] Secrets dans Vault/Secret Manager
- [ ] MFA activé pour admins
- [ ] Audit logging activé
- [ ] Monitoring configuré
- [ ] Tests de sécurité passés
- [ ] Compliance KYC/AML validé

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

## ⚠️ Avertissements

- **AUCUN TRANSFERT RÉEL** sans credentials bancaires valides
- Mode dry-run obligatoire pour les tests
- Conformité réglementaire requise
- Audit externe recommandé

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/your-org/banking-transfer-platform/issues)
- Documentation: [docs/](docs/)
- Email: support@banking-platform.com
