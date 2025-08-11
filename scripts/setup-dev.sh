#!/bin/bash

# SwiftPay - Script de configuration développement
# Ce script configure l'environnement de développement local

set -e

echo "🚀 Configuration de l'environnement de développement SwiftPay..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Java (optionnel pour développement)
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
        log_success "Java trouvé: $JAVA_VERSION"
    else
        log_warning "Java non trouvé. Utilisez Docker pour le développement."
    fi
    
    # Node.js (optionnel pour développement frontend)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js trouvé: $NODE_VERSION"
    else
        log_warning "Node.js non trouvé. Utilisez Docker pour le développement."
    fi
    
    log_success "Prérequis vérifiés"
}

# Créer les répertoires nécessaires
create_directories() {
    log_info "Création des répertoires..."
    
    mkdir -p {backend/logs,backend/certificates,frontend/dist,database/data,infrastructure/monitoring/{prometheus,grafana,logstash}}
    mkdir -p logs/{backend,frontend,database}
    
    # Répertoires pour les certificats de développement
    mkdir -p certificates/{dev,test}
    
    log_success "Répertoires créés"
}

# Configurer les variables d'environnement
setup_environment() {
    log_info "Configuration des variables d'environnement..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        log_success "Fichier .env créé depuis .env.example"
    else
        log_warning "Fichier .env existe déjà"
    fi
    
    # Générer des secrets pour le développement
    if [ ! -f .env.local ]; then
        cat > .env.local << EOF
# Secrets générés pour le développement local
JWT_SECRET=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)
CSRF_SECRET=$(openssl rand -base64 32)
WEBHOOK_SECRET=$(openssl rand -base64 32)
EOF
        log_success "Secrets de développement générés dans .env.local"
    fi
}

# Créer les certificats de développement
create_dev_certificates() {
    log_info "Création des certificats de développement..."
    
    CERT_DIR="./certificates/dev"
    
    if [ ! -f "$CERT_DIR/swift-client.p12" ]; then
        # Créer une CA de développement
        openssl req -new -x509 -days 365 -nodes \
            -subj "/C=US/ST=Dev/L=Dev/O=SwiftPay Dev/CN=SwiftPay Dev CA" \
            -keyout "$CERT_DIR/ca-key.pem" \
            -out "$CERT_DIR/ca-cert.pem"
        
        # Créer le certificat client
        openssl req -new -nodes \
            -subj "/C=US/ST=Dev/L=Dev/O=SwiftPay Dev/CN=SwiftPay Client" \
            -keyout "$CERT_DIR/client-key.pem" \
            -out "$CERT_DIR/client-req.pem"
        
        # Signer le certificat client
        openssl x509 -req -in "$CERT_DIR/client-req.pem" \
            -CA "$CERT_DIR/ca-cert.pem" \
            -CAkey "$CERT_DIR/ca-key.pem" \
            -CAcreateserial \
            -out "$CERT_DIR/client-cert.pem" \
            -days 365
        
        # Créer le PKCS12
        openssl pkcs12 -export \
            -in "$CERT_DIR/client-cert.pem" \
            -inkey "$CERT_DIR/client-key.pem" \
            -out "$CERT_DIR/swift-client.p12" \
            -password pass:devpassword
        
        # Nettoyer les fichiers temporaires
        rm "$CERT_DIR/client-req.pem"
        
        log_success "Certificats de développement créés"
    else
        log_warning "Certificats de développement existent déjà"
    fi
}

# Configurer la base de données
setup_database() {
    log_info "Configuration de la base de données..."
    
    # Créer le script d'initialisation
    cat > database/init/init.sql << EOF
-- Initialisation de la base de données SwiftPay
CREATE DATABASE keycloak;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO swiftpay;

-- Créer les extensions nécessaires
\c swiftpay;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Utilisateur pour Keycloak
\c keycloak;
-- Keycloak gérera ses propres tables
EOF
    
    log_success "Configuration de base de données préparée"
}

# Configurer Prometheus
setup_prometheus() {
    log_info "Configuration de Prometheus..."
    
    cat > infrastructure/monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "swiftpay.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093

scrape_configs:
  # SwiftPay Backend
  - job_name: 'swiftpay-backend'
    static_configs:
      - targets: ['backend:8081']
    metrics_path: '/actuator/prometheus'
    scrape_interval: 30s

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  # Prometheus lui-même
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

    # Règles d'alerte
    cat > infrastructure/monitoring/prometheus/swiftpay.rules.yml << EOF
groups:
  - name: swiftpay.rules
    rules:
      - alert: SwiftPayBackendDown
        expr: up{job="swiftpay-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "SwiftPay Backend est down"
          description: "Le backend SwiftPay n'est pas accessible depuis {{ \$labels.instance }}"

      - alert: HighTransferFailureRate
        expr: rate(transfer_failures_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Taux d'échec de transfert élevé"
          description: "{{ \$value }} transferts échouent par seconde"

      - alert: DatabaseConnectionHigh
        expr: hikaricp_connections_active / hikaricp_connections_max > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation élevée des connexions DB"
          description: "{{ \$value }}% des connexions DB sont utilisées"
EOF

    log_success "Configuration Prometheus créée"
}

# Configurer Grafana
setup_grafana() {
    log_info "Configuration de Grafana..."
    
    mkdir -p infrastructure/monitoring/grafana/{dashboards,datasources}
    
    # Configuration des datasources
    cat > infrastructure/monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    # Dashboard SwiftPay
    cat > infrastructure/monitoring/grafana/dashboards/swiftpay.json << EOF
{
  "dashboard": {
    "id": null,
    "title": "SwiftPay Dashboard",
    "tags": ["swiftpay"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Transferts par Statut",
        "type": "stat",
        "targets": [
          {
            "expr": "sum by (status) (transfer_total)",
            "legendFormat": "{{status}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Volume de Transferts",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(transfer_volume_total[5m]))",
            "legendFormat": "Volume/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      }
    ],
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

    log_success "Configuration Grafana créée"
}

# Configurer Logstash
setup_logstash() {
    log_info "Configuration de Logstash..."
    
    cat > infrastructure/monitoring/logstash/logstash.conf << EOF
input {
  beats {
    port => 5044
  }
  
  # Logs du backend SwiftPay
  file {
    path => "/app/logs/swiftpay.log"
    start_position => "beginning"
    codec => "json"
    tags => ["swiftpay", "backend"]
  }
}

filter {
  if "swiftpay" in [tags] {
    # Parser les logs JSON
    json {
      source => "message"
    }
    
    # Extraire le correlation ID
    if [correlationId] {
      mutate {
        add_tag => ["correlated"]
      }
    }
    
    # Classifier les logs de sécurité
    if [logger] =~ /Security|Auth|Swift/ {
      mutate {
        add_tag => ["security"]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "swiftpay-logs-%{+YYYY.MM.dd}"
  }
  
  # Debug en développement
  stdout {
    codec => rubydebug
  }
}
EOF

    log_success "Configuration Logstash créée"
}

# Créer les scripts utilitaires
create_utility_scripts() {
    log_info "Création des scripts utilitaires..."
    
    # Script de test SWIFT
    cat > scripts/swift-test.sh << 'EOF'
#!/bin/bash
# Script de test de connectivité SWIFT

ENDPOINT=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --endpoint)
            ENDPOINT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Usage: $0 [--endpoint URL] [--dry-run]"
            exit 1
            ;;
    esac
done

if [ -z "$ENDPOINT" ]; then
    ENDPOINT="http://localhost:8080/api"
fi

echo "🧪 Test de connectivité SWIFT..."
echo "Endpoint: $ENDPOINT"
echo "Mode dry-run: $DRY_RUN"

# Test de l'API de test
curl -X POST "$ENDPOINT/admin/swift/test-connectivity" \
    -H "Content-Type: application/json" \
    -d '{
        "testTransfer": {
            "amount": 1.00,
            "currency": "USD",
            "recipientBic": "TESTBICXXX",
            "recipientName": "Test Connectivity"
        }
    }' | jq .

echo "✅ Test terminé"
EOF

    chmod +x scripts/swift-test.sh
    
    # Script de vérification des certificats
    cat > scripts/certificate-check.sh << 'EOF'
#!/bin/bash
# Vérification des certificats SWIFT

CERT_DIR="./certificates/dev"

echo "🔍 Vérification des certificats..."

# Vérifier le certificat client
if [ -f "$CERT_DIR/swift-client.p12" ]; then
    echo "Certificat client trouvé"
    openssl pkcs12 -in "$CERT_DIR/swift-client.p12" -info -noout -passin pass:devpassword
else
    echo "❌ Certificat client non trouvé"
    exit 1
fi

# Vérifier le certificat CA
if [ -f "$CERT_DIR/ca-cert.pem" ]; then
    echo "Certificat CA trouvé"
    openssl x509 -in "$CERT_DIR/ca-cert.pem" -dates -noout
else
    echo "❌ Certificat CA non trouvé"
    exit 1
fi

echo "✅ Certificats vérifiés"
EOF

    chmod +x scripts/certificate-check.sh
    
    log_success "Scripts utilitaires créés"
}

# Installer les dépendances
install_dependencies() {
    log_info "Installation des dépendances..."
    
    # Backend (si Java disponible)
    if command -v mvn &> /dev/null && [ -f backend/pom.xml ]; then
        log_info "Installation des dépendances Maven..."
        cd backend
        ./mvnw dependency:go-offline
        cd ..
        log_success "Dépendances Maven installées"
    fi
    
    # Frontend (si Node.js disponible)
    if command -v npm &> /dev/null && [ -f frontend/package.json ]; then
        log_info "Installation des dépendances npm..."
        cd frontend
        npm install
        cd ..
        log_success "Dépendances npm installées"
    fi
}

# Initialiser les services Docker
init_docker_services() {
    log_info "Initialisation des services Docker..."
    
    # Arrêter les services existants
    docker-compose down -v 2>/dev/null || true
    
    # Construire les images
    log_info "Construction des images Docker..."
    docker-compose build --no-cache
    
    # Démarrer les services de base (DB, Redis, Vault)
    log_info "Démarrage des services de base..."
    docker-compose up -d postgres redis vault keycloak
    
    # Attendre que les services soient prêts
    log_info "Attente de la disponibilité des services..."
    
    # Attendre PostgreSQL
    while ! docker-compose exec postgres pg_isready -U swiftpay -d swiftpay &>/dev/null; do
        echo -n "."
        sleep 2
    done
    echo ""
    log_success "PostgreSQL prêt"
    
    # Attendre Redis
    while ! docker-compose exec redis redis-cli -a redis123 ping &>/dev/null; do
        echo -n "."
        sleep 2
    done
    echo ""
    log_success "Redis prêt"
    
    # Attendre Vault
    while ! curl -s http://localhost:8200/v1/sys/health &>/dev/null; do
        echo -n "."
        sleep 2
    done
    echo ""
    log_success "Vault prêt"
    
    # Attendre Keycloak
    while ! curl -s http://localhost:8180/health &>/dev/null; do
        echo -n "."
        sleep 5
    done
    echo ""
    log_success "Keycloak prêt"
}

# Configurer Vault pour le développement
setup_vault_dev() {
    log_info "Configuration de Vault pour le développement..."
    
    # Activer le moteur KV
    docker-compose exec vault vault secrets enable -path=secret kv-v2 || true
    
    # Stocker des secrets de développement
    docker-compose exec vault vault kv put secret/swiftpay/database \
        password="swiftpay123"
    
    docker-compose exec vault vault kv put secret/swiftpay/swift \
        client_cert_password="devpassword" \
        api_key="dev-api-key"
    
    docker-compose exec vault vault kv put secret/swiftpay/encryption \
        master_key="$(openssl rand -base64 32)"
    
    log_success "Vault configuré"
}

# Configurer Keycloak
setup_keycloak_dev() {
    log_info "Configuration de Keycloak pour le développement..."
    
    # Attendre que Keycloak soit complètement prêt
    sleep 30
    
    log_warning "Configuration manuelle de Keycloak requise:"
    log_warning "1. Aller sur http://localhost:8180"
    log_warning "2. Se connecter avec admin/admin123"
    log_warning "3. Créer le realm 'swiftpay'"
    log_warning "4. Configurer les clients 'swiftpay-backend' et 'swiftpay-frontend'"
    log_warning "5. Créer les rôles: user, operator, admin"
    log_warning "6. Créer un utilisateur de test"
}

# Démarrer tous les services
start_all_services() {
    log_info "Démarrage de tous les services..."
    
    docker-compose up -d
    
    log_success "Tous les services démarrés"
    
    echo ""
    echo "🎉 Environnement de développement configuré avec succès!"
    echo ""
    echo "📊 Services disponibles:"
    echo "  • Frontend:     http://localhost:3000"
    echo "  • Backend API:  http://localhost:8080"
    echo "  • Swagger UI:   http://localhost:8080/swagger-ui.html"
    echo "  • Keycloak:     http://localhost:8180"
    echo "  • Vault:        http://localhost:8200"
    echo "  • Grafana:      http://localhost:3001 (admin/admin123)"
    echo "  • Prometheus:   http://localhost:9090"
    echo "  • Kibana:       http://localhost:5601"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "  1. Configurer Keycloak (voir instructions ci-dessus)"
    echo "  2. Tester l'API: curl http://localhost:8080/api/actuator/health"
    echo "  3. Consulter les logs: docker-compose logs -f backend"
    echo ""
    echo "⚠️  Pour SWIFT en production:"
    echo "  • Consultez ONBOARDING_SWIFT.md"
    echo "  • Obtenez les credentials de votre banque"
    echo "  • Configurez les certificats de production"
}

# Fonction principale
main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    SwiftPay Setup Script                    ║"
    echo "║          Configuration Environnement de Développement       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    check_prerequisites
    create_directories
    setup_environment
    create_dev_certificates
    setup_database
    setup_prometheus
    setup_grafana
    setup_logstash
    create_utility_scripts
    install_dependencies
    init_docker_services
    setup_vault_dev
    setup_keycloak_dev
    start_all_services
    
    echo ""
    echo "🎯 Configuration terminée! Consultez le README.md pour plus d'informations."
}

# Exécuter le script principal
main "$@"