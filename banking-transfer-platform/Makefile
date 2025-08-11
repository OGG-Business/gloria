# Banking Transfer Platform Makefile

.PHONY: help install build up down logs clean test lint format migrate seed

# Default target
help:
	@echo "Banking Transfer Platform - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install all dependencies"
	@echo "  build       - Build all Docker images"
	@echo "  up          - Start all services"
	@echo "  down        - Stop all services"
	@echo "  logs        - Show logs for all services"
	@echo "  clean       - Clean up containers, images, and volumes"
	@echo ""
	@echo "Backend:"
	@echo "  backend-up  - Start only backend services"
	@echo "  backend-logs- Show backend logs"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with test data"
	@echo ""
	@echo "Testing:"
	@echo "  test        - Run all tests"
	@echo "  test-backend- Run backend tests"
	@echo "  test-frontend- Run frontend tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo ""
	@echo "Monitoring:"
	@echo "  monitoring  - Start monitoring stack only"
	@echo "  logs-monitoring- Show monitoring logs"
	@echo ""
	@echo "Production:"
	@echo "  prod-build  - Build for production"
	@echo "  prod-up     - Start production stack"

# Development commands
install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting all services..."
	docker-compose up -d

down:
	@echo "Stopping all services..."
	docker-compose down

logs:
	@echo "Showing logs..."
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v --rmi all
	docker system prune -f

# Backend commands
backend-up:
	@echo "Starting backend services..."
	docker-compose up -d postgres redis backend

backend-logs:
	@echo "Showing backend logs..."
	docker-compose logs -f backend

migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

seed:
	@echo "Seeding database..."
	docker-compose exec backend python -m app.scripts.seed

# Testing commands
test:
	@echo "Running all tests..."
	@echo "Backend tests..."
	cd backend && pytest
	@echo "Frontend tests..."
	cd frontend && npm test

test-backend:
	@echo "Running backend tests..."
	cd backend && pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Code quality commands
lint:
	@echo "Running linting..."
	@echo "Backend linting..."
	cd backend && flake8 app/ && mypy app/
	@echo "Frontend linting..."
	cd frontend && npm run lint

format:
	@echo "Formatting code..."
	@echo "Backend formatting..."
	cd backend && black app/ && isort app/
	@echo "Frontend formatting..."
	cd frontend && npm run format

# Monitoring commands
monitoring:
	@echo "Starting monitoring stack..."
	docker-compose up -d prometheus grafana jaeger elasticsearch kibana filebeat

logs-monitoring:
	@echo "Showing monitoring logs..."
	docker-compose logs -f prometheus grafana jaeger elasticsearch kibana filebeat

# Production commands
prod-build:
	@echo "Building for production..."
	docker-compose -f docker-compose.prod.yml build

prod-up:
	@echo "Starting production stack..."
	docker-compose -f docker-compose.prod.yml up -d

# Utility commands
health-check:
	@echo "Checking service health..."
	@echo "Backend health:"
	curl -f http://localhost:8000/health || echo "Backend not healthy"
	@echo "Frontend health:"
	curl -f http://localhost:3000 || echo "Frontend not healthy"
	@echo "Database health:"
	docker-compose exec postgres pg_isready -U banking_user -d banking_transfer || echo "Database not healthy"

backup:
	@echo "Creating database backup..."
	docker-compose exec postgres pg_dump -U banking_user banking_transfer > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	docker-compose exec -T postgres psql -U banking_user -d banking_transfer < $$backup_file

# Development shortcuts
dev: install build up
	@echo "Development environment ready!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Grafana: http://localhost:3001"
	@echo "Kibana: http://localhost:5601"

quick-test:
	@echo "Running quick tests..."
	docker-compose exec backend pytest -xvs

# Database commands
db-reset:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	sleep 10
	docker-compose exec postgres psql -U banking_user -d banking_transfer -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	make migrate
	make seed

# Security commands
security-scan:
	@echo "Running security scan..."
	docker-compose exec backend bandit -r app/
	docker-compose exec backend safety check

# Performance commands
load-test:
	@echo "Running load test..."
	docker-compose exec backend python -m app.scripts.load_test

# Documentation commands
docs:
	@echo "Generating documentation..."
	cd backend && pdoc --html app/
	@echo "Documentation generated in backend/html/"

# Deployment commands
deploy-staging:
	@echo "Deploying to staging..."
	docker-compose -f docker-compose.staging.yml up -d

deploy-production:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d