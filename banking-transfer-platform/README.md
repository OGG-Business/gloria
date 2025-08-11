# Plateforme de Transferts Bancaires - Banking Transfer Platform

Système complet de transferts bancaires internationaux conforme aux standards SWIFT et ISO 20022, spécialement conçu pour les banques opérant en RDC et en Afrique.

## 🏗️ Architecture

### Microservices
- **Auth Service**: Authentification OAuth2/OpenID Connect (Keycloak)
- **Accounts Service**: Gestion des comptes bancaires
- **Transfers Service**: Orchestration des transferts
- **Connectors Service**: Connecteurs SWIFT et Mojaloop
- **KYC Service**: Conformité KYC/AML
- **Notifications Service**: Notifications temps réel
- **Audit Service**: Audit trail et conformité

### Technologies
- **Backend**: Spring Boot 3.x (Java 17)
- **Frontend**: React 18 + TypeScript + PWA
- **Base de données**: PostgreSQL 15 (Cloud SQL)
- **Message Broker**: Apache Kafka
- **Cache**: Redis
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Sécurité**: HashiCorp Vault + TLS 1.3

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Java 17+
- Node.js 18+
- PostgreSQL 15+

### Installation
```bash
# Cloner le projet
git clone <repository-url>
cd banking-transfer-platform

# Démarrer l'environnement de développement
docker-compose up -d

# Vérifier les services
docker-compose ps
```

### Accès aux services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **Keycloak**: http://localhost:8081
- **Grafana**: http://localhost:3001
- **Kibana**: http://localhost:5601

## 📋 Fonctionnalités

### Transferts Bancaires
- Support SWIFT MT/MX messages
- Format ISO 20022 (pacs.008, pacs.002, pacs.004)
- Validation IBAN/BIC en temps réel
- Suivi des transferts avec timeline d'événements
- Connecteurs Mojaloop pour corridors africains

### Sécurité & Conformité
- Authentification multi-facteurs (MFA)
- Chiffrement AES-256 pour données sensibles
- Audit trail complet
- Screening KYC/AML automatique
- Conformité aux réglementations bancaires

### Interface Utilisateur
- Interface responsive (desktop, tablet, mobile)
- PWA avec support offline
- Dashboard en temps réel
- Notifications push

## 🔧 Configuration

### Variables d'environnement
```bash
# Copier le template
cp .env.example .env

# Configurer les variables
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_transfers
DB_USER=postgres
DB_PASSWORD=secure_password

# SWIFT Configuration
SWIFT_BIC=YOUR_BIC
SWIFT_CERT_PATH=/path/to/cert.pem
SWIFT_KEY_PATH=/path/to/key.pem

# Vault Configuration
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=your_vault_token
```

## 🧪 Tests

```bash
# Tests unitaires
./mvnw test

# Tests d'intégration
./mvnw verify

# Tests de sécurité
./scripts/security-scan.sh
```

## 📊 Monitoring

### Métriques disponibles
- Taux de succès des transferts
- Temps de traitement
- Erreurs par type
- Utilisation des ressources

### Alertes configurées
- Transferts échoués > 5%
- Temps de réponse > 30s
- Erreurs de connectivité SWIFT

## 🔒 Sécurité

### Bonnes pratiques implémentées
- Chiffrement en transit (TLS 1.3)
- Chiffrement au repos (AES-256)
- Rotation automatique des clés
- Audit trail immuable
- Validation stricte des entrées

### Checklist de sécurité
- [ ] Scan de vulnérabilités OWASP
- [ ] Tests de pénétration
- [ ] Audit de code sécurité
- [ ] Conformité PCI DSS
- [ ] Tests de charge

## 📚 Documentation

- [Guide d'installation](docs/INSTALLATION.md)
- [Configuration SWIFT](docs/ONBOARDING_SWIFT.md)
- [API Reference](docs/API.md)
- [Architecture détaillée](docs/ARCHITECTURE.md)
- [Guide de sécurité](docs/SECURITY.md)

## 🤝 Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines de contribution.

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## ⚠️ Avertissement

**IMPORTANT**: Ce système est conçu pour des transferts bancaires réels. Assurez-vous d'avoir les autorisations nécessaires et les accords contractuels avec les banques avant toute utilisation en production.

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/your-org/banking-transfer-platform/issues)
- Documentation: [Wiki](https://github.com/your-org/banking-transfer-platform/wiki)
- Email: support@banking-transfer-platform.com