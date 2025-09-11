# Makefile for Polaris Platform
# Provides project management targets for development and deployment

.PHONY: help bootstrap install clean lint test migrate seed run run-dev build docker health docs

# Configuration
PYTHON := python3
PIP := pip3
VENV := venv
SRC_DIR := backend
FRONTEND_DIR := frontend
MONGO_URL ?= mongodb://localhost:27017
DB_NAME ?= polaris_dev
SERVICE_NAME ?= polaris-platform

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Polaris Platform Development Commands$(NC)"
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

bootstrap: ## Bootstrap development environment
	@echo "$(BLUE)Bootstrapping Polaris development environment...$(NC)"
	@if [ ! -d $(VENV) ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "$(YELLOW)Activating virtual environment and installing dependencies...$(NC)"
	@. $(VENV)/bin/activate && \
		$(PIP) install --upgrade pip && \
		$(PIP) install -r $(SRC_DIR)/requirements.txt
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Run 'make migrate' to set up the database"
	@echo "  2. Run 'make seed' to populate with sample data"
	@echo "  3. Run 'make run-dev' to start the development server"

install: ## Install/update dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@. $(VENV)/bin/activate && $(PIP) install -r $(SRC_DIR)/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

lint: ## Run code linting and formatting
	@echo "$(BLUE)Running code linting...$(NC)"
	@. $(VENV)/bin/activate && \
		echo "$(YELLOW)Running black...$(NC)" && \
		black --check $(SRC_DIR) || (echo "$(RED)✗ Black formatting issues found. Run 'black $(SRC_DIR)' to fix.$(NC)" && exit 1) && \
		echo "$(YELLOW)Running isort...$(NC)" && \
		isort --check-only $(SRC_DIR) || (echo "$(RED)✗ Import sorting issues found. Run 'isort $(SRC_DIR)' to fix.$(NC)" && exit 1) && \
		echo "$(YELLOW)Running flake8...$(NC)" && \
		flake8 $(SRC_DIR) && \
		echo "$(YELLOW)Running mypy...$(NC)" && \
		mypy $(SRC_DIR) --ignore-missing-imports
	@echo "$(GREEN)✓ Linting passed$(NC)"

format: ## Auto-format code
	@echo "$(BLUE)Formatting code...$(NC)"
	@. $(VENV)/bin/activate && \
		black $(SRC_DIR) && \
		isort $(SRC_DIR)
	@echo "$(GREEN)✓ Code formatted$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	@. $(VENV)/bin/activate && \
		pytest tests/ -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	@. $(VENV)/bin/activate && \
		pytest tests/unit/ -v
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	@. $(VENV)/bin/activate && \
		pytest tests/integration/ -v
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		MONGO_URL=$(MONGO_URL) DB_NAME=$(DB_NAME) \
		$(PYTHON) -m migrations.migrate migrate --verbose
	@echo "$(GREEN)✓ Migrations completed$(NC)"

migrate-status: ## Show migration status
	@echo "$(BLUE)Checking migration status...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		MONGO_URL=$(MONGO_URL) DB_NAME=$(DB_NAME) \
		$(PYTHON) -m migrations.migrate status

rollback: ## Rollback to specific migration (usage: make rollback TARGET=001)
	@if [ -z "$(TARGET)" ]; then \
		echo "$(RED)Error: TARGET migration version required$(NC)"; \
		echo "Usage: make rollback TARGET=001"; \
		exit 1; \
	fi
	@echo "$(BLUE)Rolling back to migration $(TARGET)...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		MONGO_URL=$(MONGO_URL) DB_NAME=$(DB_NAME) \
		$(PYTHON) -m migrations.migrate rollback --target=$(TARGET) --verbose
	@echo "$(GREEN)✓ Rollback completed$(NC)"

seed: ## Populate database with seed data
	@echo "$(BLUE)Seeding database with sample data...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		MONGO_URL=$(MONGO_URL) DB_NAME=$(DB_NAME) \
		$(PYTHON) scripts/seed.py
	@echo "$(GREEN)✓ Database seeded$(NC)"

run: ## Run the application server
	@echo "$(BLUE)Starting Polaris server...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		MONGO_URL=$(MONGO_URL) DB_NAME=$(DB_NAME) \
		uvicorn server:app --host 0.0.0.0 --port 8000

run-dev: ## Run development server with auto-reload
	@echo "$(BLUE)Starting Polaris development server...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		ENVIRONMENT=development \
		MONGO_URL=$(MONGO_URL) \
		DB_NAME=$(DB_NAME) \
		LOG_LEVEL=DEBUG \
		ENABLE_TRACING=true \
		uvicorn server:app --host 0.0.0.0 --port 8000 --reload

run-worker: ## Run background worker for outbox processing
	@echo "$(BLUE)Starting background worker...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		MONGO_URL=$(MONGO_URL) DB_NAME=$(DB_NAME) \
		$(PYTHON) scripts/worker.py

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	@curl -s http://localhost:8000/health/system | python -m json.tool || \
		echo "$(RED)✗ Health check failed - is the server running?$(NC)"

health-db: ## Check database health
	@echo "$(BLUE)Checking database health...$(NC)"
	@curl -s http://localhost:8000/health/database | python -m json.tool || \
		echo "$(RED)✗ Database health check failed$(NC)"

build: ## Build application for production
	@echo "$(BLUE)Building application...$(NC)"
	@. $(VENV)/bin/activate && \
		$(PIP) install --upgrade pip setuptools wheel && \
		$(PIP) install -r $(SRC_DIR)/requirements.txt --no-deps
	@echo "$(GREEN)✓ Build completed$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t $(SERVICE_NAME):latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run application in Docker
	@echo "$(BLUE)Running application in Docker...$(NC)"
	@docker run -p 8000:8000 \
		-e MONGO_URL=$(MONGO_URL) \
		-e DB_NAME=$(DB_NAME) \
		-e ENVIRONMENT=development \
		$(SERVICE_NAME):latest

docker-compose-up: ## Start services with docker-compose
	@echo "$(BLUE)Starting services with docker-compose...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(YELLOW)Application will be available at http://localhost:8000$(NC)"
	@echo "$(YELLOW)MongoDB will be available at localhost:27017$(NC)"
	@echo "$(YELLOW)Jaeger UI will be available at http://localhost:16686$(NC)"

docker-compose-down: ## Stop docker-compose services
	@echo "$(BLUE)Stopping docker-compose services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-compose-logs: ## Show docker-compose logs
	@docker-compose logs -f

otel: ## Start OpenTelemetry collector and Jaeger
	@echo "$(BLUE)Starting OpenTelemetry stack...$(NC)"
	@docker-compose -f docker-compose.otel.yml up -d
	@echo "$(GREEN)✓ OpenTelemetry stack started$(NC)"
	@echo "$(YELLOW)Jaeger UI: http://localhost:16686$(NC)"

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	@. $(VENV)/bin/activate && \
		cd $(SRC_DIR) && \
		$(PYTHON) scripts/benchmark.py
	@echo "$(GREEN)✓ Benchmarks completed$(NC)"

security-scan: ## Run security vulnerability scan
	@echo "$(BLUE)Running security scan...$(NC)"
	@. $(VENV)/bin/activate && \
		safety check --json || echo "$(YELLOW)Security scan completed with warnings$(NC)"
	@echo "$(GREEN)✓ Security scan completed$(NC)"

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@. $(VENV)/bin/activate && \
		cd docs && \
		sphinx-build -b html source build
	@echo "$(GREEN)✓ Documentation generated in docs/build/$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8080$(NC)"
	@cd docs/build && $(PYTHON) -m http.server 8080

pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	@make clean
	@make lint
	@make test-unit
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

# Development workflow targets
dev-setup: bootstrap migrate seed ## Complete development setup
	@echo "$(GREEN)✓ Development environment fully configured$(NC)"
	@echo "$(YELLOW)Run 'make run-dev' to start the development server$(NC)"

ci: clean lint test ## Run CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline completed successfully$(NC)"

deploy-staging: ## Deploy to staging environment (placeholder)
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "$(YELLOW)Staging deployment not implemented yet$(NC)"

deploy-prod: ## Deploy to production environment (placeholder)
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(YELLOW)Production deployment not implemented yet$(NC)"

# Utility targets
logs: ## Show application logs
	@tail -f /var/log/polaris/application.log 2>/dev/null || \
		echo "$(YELLOW)No log file found. Is the application running?$(NC)"

ps: ## Show running processes
	@ps aux | grep -E "(polaris|uvicorn|python)" | grep -v grep || \
		echo "$(YELLOW)No Polaris processes found$(NC)"

env: ## Show environment configuration
	@echo "$(BLUE)Environment Configuration:$(NC)"
	@echo "MONGO_URL: $(MONGO_URL)"
	@echo "DB_NAME: $(DB_NAME)"
	@echo "SERVICE_NAME: $(SERVICE_NAME)"
	@echo "PYTHON: $(shell which $(PYTHON))"
	@echo "Virtual Environment: $(shell [ -d $(VENV) ] && echo "Present" || echo "Missing")"

# Default target
.DEFAULT_GOAL := help