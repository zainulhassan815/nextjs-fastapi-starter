.PHONY: up down restart logs build migrate makemigrations seed generate-client dev dev-frontend db-shell redis-shell lint format clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Docker ---
up: ## Start backend services (db, backend, etc.)
	cp -n .env.example .env 2>/dev/null || true
	docker compose up -d --build

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Tail logs (use s=<service> for specific, e.g. make logs s=backend)
	docker compose logs -f $(s)

build: ## Rebuild all containers (no cache)
	docker compose build --no-cache

# --- Database ---
migrate: ## Run alembic migrations
	docker compose exec backend uv run alembic upgrade head

makemigrations: ## Create new migration (use m="message")
	docker compose exec backend uv run alembic revision --autogenerate -m "$(m)"

seed: ## Seed database with test data
	docker compose exec backend uv run python -m scripts.seed

db-shell: ## Open psql shell
	docker compose exec db psql -U hackathon -d hackathon

# --- Redis ---
redis-shell: ## Open redis-cli
	docker compose exec redis redis-cli

# --- Frontend ---
dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# --- API Client ---
generate-client: ## Generate TypeScript API client from OpenAPI spec
	./scripts/generate-api-client.sh

# --- Development ---
dev: up ## Start everything (backend services + frontend)
	@echo "Backend running at http://localhost:8000"
	@echo "Starting frontend..."
	cd frontend && npm run dev

# --- Code Quality ---
lint: ## Lint backend and frontend
	docker compose exec backend uv run ruff check app/
	cd frontend && npm run lint

format: ## Format backend code
	docker compose exec backend uv run ruff format app/

# --- Cleanup ---
clean: ## Remove all containers, volumes, and generated files
	docker compose down -v --remove-orphans
	rm -rf frontend/.next frontend/node_modules frontend/lib/api/generated
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
