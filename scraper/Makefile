.PHONY: help build up down logs shell db-shell clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

up-admin: ## Start all services including pgAdmin
	docker-compose --profile admin up -d

down: ## Stop all services
	docker-compose down

logs: ## Follow scraper logs
	docker-compose logs -f scraper

logs-all: ## Follow all services logs
	docker-compose logs -f

shell: ## Open shell in scraper container
	docker-compose exec scraper /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U scraper -d scraper_db

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli -a redis_password_2024

run-once: ## Run scraper once and exit
	docker-compose run -e RUN_MODE=once --rm scraper

stats: ## Show database statistics
	docker-compose exec postgres psql -U scraper -d scraper_db -c "SELECT source, COUNT(*) as total FROM articles GROUP BY source;"

clean: ## Remove containers, volumes, and images
	docker-compose down -v
	docker system prune -f

clean-data: ## Clean scraped data
	rm -rf data/raw/* data/processed/* data/images/*/* logs/*

backup-db: ## Backup database
	docker-compose exec postgres pg_dump -U scraper scraper_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$$(date +%Y%m%d_%H%M%S).sql"

restore-db: ## Restore database (usage: make restore-db FILE=backup.sql)
	docker-compose exec -T postgres psql -U scraper scraper_db < $(FILE)

test: ## Run tests
	docker-compose run --rm scraper pytest

test-coverage: ## Run tests with coverage
	docker-compose run --rm scraper pytest --cov=src --cov-report=html

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	playwright install chromium

format: ## Format code with black
	docker-compose run --rm scraper black src/

lint: ## Lint code with flake8
	docker-compose run --rm scraper flake8 src/

setup: ## Initial setup (copy .env, build, start)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your settings."; \
	fi
	@make build
	@make up
	@echo "Setup complete! Services are starting..."
	@echo "Run 'make logs' to see the logs"
