.PHONY: help build up down logs dev clean restart test lint typecheck shell ps inspect

SERVICE ?= export-api

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker compose build

up: ## Start all services in detached mode
	docker compose up --build -d

down: ## Stop and remove all containers
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

dev: ## Start services with live output
	docker compose up --build

clean: ## Stop all containers and remove volumes
	docker compose down -v

restart: down up ## Restart all services

test: ## Run all tests with coverage
	python -m pytest tests/ shared/src/shared/ services/*/tests/ -v --cov

lint: ## Lint all Python files with ruff
	ruff check services/ shared/ scripts/

typecheck: ## Run mypy type checker
	mypy services/ shared/ --pretty

shell: ## Open a shell in a running container
	docker compose exec $(SERVICE) /bin/sh

ps: ## Show running containers
	docker compose ps

inspect: ## Inspect job state (usage: make inspect JOB_ID=JOB-20260713-abc12)
	@[ -n "$(JOB_ID)" ] && cat data/jobs/$(JOB_ID).json 2>/dev/null || echo "Usage: make inspect JOB_ID=JOB-YYYYMMDD-XXXXX"
