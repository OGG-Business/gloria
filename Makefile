# Makefile pour Banking Transfer Platform

.PHONY: help build up down logs clean test lint format migrate seed

# Variables
COMPOSE_FILE = docker-compose.yml
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Couleurs pour les messages
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Afficher l'aide
	@echo "$(GREEN)Banking Transfer Platform - Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Développement
build: ## Construire les images Docker
	@echo "$(GREEN)Construction des images Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Démarrer tous les services
	@echo "$(GREEN)Démarrage des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Arrêter tous les services
	@echo "$(YELLOW)Arrêt des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

logs: ## Afficher les logs de tous les services
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## Afficher les logs du backend
	docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend: ## Afficher les logs du frontend
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

logs-db: ## Afficher les logs de la base de données
	docker-compose -f $(COMPOSE_FILE) logs -f postgres

# Base de données
migrate: ## Exécuter les migrations de base de données
	@echo "$(GREEN)Exécution des migrations...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m alembic upgrade head

migrate-create: ## Créer une nouvelle migration
	@echo "$(GREEN)Création d'une nouvelle migration...$(NC)"
	@read -p "Nom de la migration: " name; \
	docker-compose -f $(COMPOSE_FILE) exec backend python -m alembic revision --autogenerate -m "$$name"

migrate-rollback: ## Annuler la dernière migration
	@echo "$(YELLOW)Annulation de la dernière migration...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m alembic downgrade -1

seed: ## Peupler la base de données avec des données de test
	@echo "$(GREEN)Peuplement de la base de données...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m scripts.seed_data

# Tests
test: ## Exécuter tous les tests
	@echo "$(GREEN)Exécution des tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend pytest

test-unit: ## Exécuter les tests unitaires
	@echo "$(GREEN)Exécution des tests unitaires...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend pytest tests/unit/

test-integration: ## Exécuter les tests d'intégration
	@echo "$(GREEN)Exécution des tests d'intégration...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend pytest tests/integration/

test-coverage: ## Exécuter les tests avec couverture
	@echo "$(GREEN)Exécution des tests avec couverture...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend pytest --cov=app --cov-report=html --cov-report=term

# Qualité du code
lint: ## Vérifier la qualité du code
	@echo "$(GREEN)Vérification de la qualité du code...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend flake8 app/
	docker-compose -f $(COMPOSE_FILE) exec backend black --check app/
	docker-compose -f $(COMPOSE_FILE) exec backend isort --check-only app/

format: ## Formater le code
	@echo "$(GREEN)Formatage du code...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend black app/
	docker-compose -f $(COMPOSE_FILE) exec backend isort app/

# Sécurité
security-scan: ## Scanner les vulnérabilités de sécurité
	@echo "$(GREEN)Scan de sécurité...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend bandit -r app/
	docker-compose -f $(COMPOSE_FILE) exec backend safety check

# Monitoring
monitoring: ## Ouvrir les interfaces de monitoring
	@echo "$(GREEN)Interfaces de monitoring:$(NC)"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana: http://localhost:3001 (admin/admin)"
	@echo "  Kibana: http://localhost:5601"
	@echo "  Keycloak: http://localhost:8080 (admin/admin)"

health: ## Vérifier la santé des services
	@echo "$(GREEN)Vérification de la santé des services...$(NC)"
	@echo "Backend:"
	@curl -s http://localhost:8000/health | jq . || echo "$(RED)Backend non accessible$(NC)"
	@echo "Frontend:"
	@curl -s http://localhost:3000 | head -1 || echo "$(RED)Frontend non accessible$(NC)"

# Utilitaires
shell-backend: ## Ouvrir un shell dans le conteneur backend
	docker-compose -f $(COMPOSE_FILE) exec backend bash

shell-db: ## Ouvrir un shell dans la base de données
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U banking_user -d banking

restart: ## Redémarrer tous les services
	@echo "$(YELLOW)Redémarrage des services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

clean: ## Nettoyer les conteneurs et volumes
	@echo "$(RED)Nettoyage complet...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f

clean-images: ## Nettoyer les images Docker
	@echo "$(RED)Nettoyage des images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --rmi all

# Production
build-prod: ## Construire les images de production
	@echo "$(GREEN)Construction des images de production...$(NC)"
	docker-compose -f docker-compose.prod.yml build

deploy-prod: ## Déployer en production
	@echo "$(GREEN)Déploiement en production...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d

# SWIFT
swift-test: ## Tester la connectivité SWIFT
	@echo "$(GREEN)Test de connectivité SWIFT...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m scripts.test_swift_connectivity

swift-send-test: ## Envoyer un message SWIFT de test
	@echo "$(GREEN)Envoi d'un message SWIFT de test...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m scripts.send_test_swift_message

# Mojaloop
mojaloop-test: ## Tester la connectivité Mojaloop
	@echo "$(GREEN)Test de connectivité Mojaloop...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m scripts.test_mojaloop_connectivity

# Documentation
docs: ## Générer la documentation
	@echo "$(GREEN)Génération de la documentation...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec backend python -m scripts.generate_docs

openapi: ## Générer la spécification OpenAPI
	@echo "$(GREEN)Génération de la spécification OpenAPI...$(NC)"
	curl -s http://localhost:8000/openapi.json | jq . > docs/openapi.json

# Sauvegarde
backup: ## Sauvegarder la base de données
	@echo "$(GREEN)Sauvegarde de la base de données...$(NC)"
	@mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U banking_user banking > backups/backup_$$(date +%Y%m%d_%H%M%S).sql

restore: ## Restaurer la base de données
	@echo "$(YELLOW)Restauration de la base de données...$(NC)"
	@ls -la backups/
	@read -p "Nom du fichier de sauvegarde: " file; \
	docker-compose -f $(COMPOSE_FILE) exec -T postgres psql -U banking_user banking < backups/$$file

# Développement local
dev-setup: ## Configuration initiale pour le développement
	@echo "$(GREEN)Configuration du développement...$(NC)"
	@cp .env.example .env || echo "$(YELLOW)Fichier .env déjà présent$(NC)"
	@mkdir -p uploads certs logs
	@echo "$(GREEN)Configuration terminée. Modifiez le fichier .env selon vos besoins.$(NC)"

dev-install: ## Installer les dépendances de développement
	@echo "$(GREEN)Installation des dépendances de développement...$(NC)"
	pip install -r backend/requirements.txt
	cd frontend && npm install

# Utilitaires rapides
status: ## Afficher le statut des services
	docker-compose -f $(COMPOSE_FILE) ps

logs-tail: ## Suivre les logs en temps réel
	docker-compose -f $(COMPOSE_FILE) logs -f --tail=100

rebuild: ## Reconstruire et redémarrer
	@echo "$(GREEN)Reconstruction et redémarrage...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	docker-compose -f $(COMPOSE_FILE) up -d

# Aide contextuelle
quick-start: ## Démarrage rapide pour les nouveaux développeurs
	@echo "$(GREEN)Démarrage rapide Banking Transfer Platform$(NC)"
	@echo "1. Configuration initiale..."
	@make dev-setup
	@echo "2. Construction des images..."
	@make build
	@echo "3. Démarrage des services..."
	@make up
	@echo "4. Attente du démarrage..."
	@sleep 30
	@echo "5. Vérification de la santé..."
	@make health
	@echo "$(GREEN)Démarrage terminé!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "Documentation API: http://localhost:8000/docs"