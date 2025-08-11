# Guide de Déploiement - Plateforme de Transferts Bancaires

## Table des matières

1. [Prérequis](#prérequis)
2. [Environnements](#environnements)
3. [Déploiement Local](#déploiement-local)
4. [Déploiement Kubernetes](#déploiement-kubernetes)
5. [Configuration de Production](#configuration-de-production)
6. [Sécurité](#sécurité)
7. [Monitoring et Observabilité](#monitoring-et-observabilité)
8. [Maintenance](#maintenance)
9. [Dépannage](#dépannage)

## Prérequis

### Système
- **OS** : Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+
- **CPU** : 4 cœurs minimum (8 recommandés)
- **RAM** : 8 GB minimum (16 GB recommandés)
- **Stockage** : 50 GB minimum

### Logiciels
- **Docker** : 20.10+
- **Docker Compose** : 2.0+
- **Kubernetes** : 1.24+ (pour déploiement K8s)
- **Helm** : 3.8+
- **Java** : 17+
- **Node.js** : 18+
- **PostgreSQL** : 14+
- **Redis** : 6.2+

### Outils de développement
- **Git** : 2.30+
- **Maven** : 3.8+
- **npm** : 8+

## Environnements

### Développement
- **Objectif** : Développement et tests locaux
- **Services** : Backend, Frontend, PostgreSQL, Redis, Kafka, Vault, Keycloak
- **Configuration** : Docker Compose

### Staging
- **Objectif** : Tests d'intégration et validation
- **Services** : Tous les services en mode test
- **Configuration** : Kubernetes avec Helm

### Production
- **Objectif** : Environnement de production
- **Services** : Tous les services avec haute disponibilité
- **Configuration** : Kubernetes avec Helm + Terraform

## Déploiement Local

### 1. Cloner le projet
```bash
git clone https://github.com/banking-transfer-platform.git
cd banking-transfer-platform
```

### 2. Configuration des variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

### 3. Démarrage des services
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f
```

### 4. Initialisation de la base de données
```bash
# Attendre que PostgreSQL soit prêt
sleep 30

# Exécuter les migrations
docker-compose exec backend ./mvnw flyway:migrate
```

### 5. Accès aux services
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8080
- **Swagger UI** : http://localhost:8080/swagger-ui
- **Keycloak** : http://localhost:8081
- **Grafana** : http://localhost:3001
- **Kibana** : http://localhost:5601

## Déploiement Kubernetes

### 1. Préparation du cluster
```bash
# Vérifier le cluster
kubectl cluster-info

# Ajouter les repositories Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add elastic https://helm.elastic.co
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
```

### 2. Configuration des secrets
```bash
# Créer le namespace
kubectl create namespace banking-transfer

# Créer les secrets
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=your-secure-password \
  -n banking-transfer

kubectl create secret generic jwt-secret \
  --from-literal=secret=your-jwt-secret-key \
  -n banking-transfer

kubectl create secret generic swift-credentials \
  --from-file=certificate=swift-cert.p12 \
  --from-literal=password=swift-cert-password \
  -n banking-transfer
```

### 3. Déploiement avec Helm
```bash
# Installer les dépendances
helm dependency build infrastructure/helm/banking-transfer-platform

# Déployer en mode développement
helm install banking-transfer infrastructure/helm/banking-transfer-platform \
  --namespace banking-transfer \
  --values infrastructure/helm/banking-transfer-platform/values-dev.yaml

# Déployer en production
helm install banking-transfer infrastructure/helm/banking-transfer-platform \
  --namespace banking-transfer \
  --values infrastructure/helm/banking-transfer-platform/values-prod.yaml
```

### 4. Vérification du déploiement
```bash
# Vérifier les pods
kubectl get pods -n banking-transfer

# Vérifier les services
kubectl get svc -n banking-transfer

# Vérifier les ingress
kubectl get ingress -n banking-transfer

# Voir les logs
kubectl logs -f deployment/banking-transfer-backend -n banking-transfer
```

## Configuration de Production

### 1. Infrastructure Cloud (GCP)
```bash
# Créer le cluster GKE
gcloud container clusters create banking-transfer-cluster \
  --zone=europe-west1-b \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10

# Configurer kubectl
gcloud container clusters get-credentials banking-transfer-cluster \
  --zone=europe-west1-b
```

### 2. Base de données Cloud SQL
```bash
# Créer l'instance PostgreSQL
gcloud sql instances create banking-transfer-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-4-16 \
  --region=europe-west1 \
  --storage-type=SSD \
  --storage-size=100GB

# Créer la base de données
gcloud sql databases create banking_transfer \
  --instance=banking-transfer-db

# Créer l'utilisateur
gcloud sql users create banking_user \
  --instance=banking-transfer-db \
  --password=your-secure-password
```

### 3. Configuration des secrets
```bash
# Utiliser Google Secret Manager
echo -n "your-jwt-secret" | gcloud secrets create jwt-secret --data-file=-

echo -n "your-db-password" | gcloud secrets create db-password --data-file=-

# Mettre à jour les secrets Kubernetes
kubectl create secret generic jwt-secret \
  --from-literal=secret="$(gcloud secrets versions access latest --secret=jwt-secret)" \
  -n banking-transfer
```

### 4. Load Balancer et SSL
```bash
# Configurer l'ingress avec SSL
kubectl apply -f infrastructure/k8s/ingress-ssl.yaml

# Obtenir un certificat SSL
kubectl apply -f infrastructure/k8s/cert-manager.yaml
```

## Sécurité

### 1. Configuration des pare-feu
```bash
# Règles de pare-feu GCP
gcloud compute firewall-rules create banking-transfer-allow-https \
  --allow tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=banking-transfer

gcloud compute firewall-rules create banking-transfer-allow-http \
  --allow tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=banking-transfer
```

### 2. Configuration Vault
```bash
# Initialiser Vault
kubectl exec -n banking-transfer vault-0 -- vault operator init

# Configurer les politiques
kubectl exec -n banking-transfer vault-0 -- vault policy write banking-transfer-policy \
  - <<EOF
path "secret/banking-transfer/*" {
  capabilities = ["read"]
}
EOF
```

### 3. Audit et conformité
```bash
# Activer l'audit Kubernetes
kubectl apply -f infrastructure/k8s/audit-policy.yaml

# Configurer les logs de sécurité
gcloud logging sinks create banking-transfer-audit \
  storage.googleapis.com/banking-transfer-audit-logs \
  --log-filter="resource.type=k8s_cluster"
```

## Monitoring et Observabilité

### 1. Prometheus et Grafana
```bash
# Déployer Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --values infrastructure/helm/prometheus-values.yaml

# Déployer Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --values infrastructure/helm/grafana-values.yaml
```

### 2. ELK Stack
```bash
# Déployer Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --values infrastructure/helm/elasticsearch-values.yaml

# Déployer Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --values infrastructure/helm/kibana-values.yaml

# Déployer Logstash
helm install logstash elastic/logstash \
  --namespace logging \
  --values infrastructure/helm/logstash-values.yaml
```

### 3. Alertes
```bash
# Configurer les alertes Prometheus
kubectl apply -f infrastructure/k8s/prometheus-rules.yaml

# Configurer les notifications Slack
kubectl apply -f infrastructure/k8s/alertmanager-config.yaml
```

## Maintenance

### 1. Sauvegarde
```bash
# Script de sauvegarde automatique
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Sauvegarde PostgreSQL
pg_dump -h $DB_HOST -U $DB_USER -d banking_transfer > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarde des fichiers de configuration
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz /etc/banking-transfer/

# Nettoyage des anciennes sauvegardes (garde 30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 2. Mise à jour
```bash
# Mise à jour avec Helm
helm upgrade banking-transfer infrastructure/helm/banking-transfer-platform \
  --namespace banking-transfer \
  --values infrastructure/helm/banking-transfer-platform/values-prod.yaml

# Rollback en cas de problème
helm rollback banking-transfer 1 -n banking-transfer
```

### 3. Monitoring de la santé
```bash
# Vérifier la santé des services
curl -f http://localhost:8080/actuator/health

# Vérifier les métriques
curl http://localhost:8080/actuator/metrics

# Vérifier les logs
kubectl logs -f deployment/banking-transfer-backend -n banking-transfer
```

## Dépannage

### 1. Problèmes courants

#### Service ne démarre pas
```bash
# Vérifier les logs
docker-compose logs service-name

# Vérifier les ressources
docker stats

# Redémarrer le service
docker-compose restart service-name
```

#### Problème de base de données
```bash
# Vérifier la connexion
docker-compose exec postgres psql -U postgres -d banking_transfer

# Vérifier les migrations
docker-compose exec backend ./mvnw flyway:info

# Réparer les migrations
docker-compose exec backend ./mvnw flyway:repair
```

#### Problème de mémoire
```bash
# Augmenter la mémoire JVM
export JAVA_OPTS="-Xmx2g -Xms1g"

# Vérifier l'utilisation mémoire
docker stats
```

### 2. Logs et diagnostics
```bash
# Collecter les logs
kubectl logs -l app=banking-transfer-backend -n banking-transfer > backend-logs.txt

# Vérifier les événements
kubectl get events -n banking-transfer

# Vérifier les ressources
kubectl top pods -n banking-transfer
```

### 3. Support
- **Documentation** : [docs/README.md](docs/README.md)
- **Issues** : [GitHub Issues](https://github.com/banking-transfer-platform/issues)
- **Email** : support@banking-transfer-platform.com

## Conclusion

Ce guide couvre les aspects essentiels du déploiement de la plateforme de transferts bancaires. Pour des configurations spécifiques ou des environnements particuliers, consultez la documentation détaillée dans le dossier `docs/`.

N'oubliez pas de :
- Tester en environnement de staging avant la production
- Configurer les sauvegardes automatiques
- Mettre en place le monitoring et les alertes
- Documenter les procédures spécifiques à votre environnement