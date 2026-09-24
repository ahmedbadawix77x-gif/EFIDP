.PHONY: help install lint format typecheck test test-cov check clean \
        up down restart logs ps health build

DOCKER=docker
COMPOSE=docker compose

help:
	@echo ""
	@echo "EFIDP — Egypt Financial Intelligence Data Platform"
	@echo "======================================================"
	@echo ""
	@echo "Developer Commands:"
	@echo "  make install     Install project and development dependencies"
	@echo "  make lint        Run Ruff linter check"
	@echo "  make format      Run Ruff format check"
	@echo "  make format-fix  Apply Ruff formatting fixes"
	@echo "  make typecheck   Run MyPy static type checking"
	@echo "  make test        Run unit test suite"
	@echo "  make test-cov    Run tests with coverage reporting"
	@echo "  make check       Run full quality gate (lint + format + type + test)"
	@echo "  make clean       Remove build, cache, and coverage artifacts"
	@echo ""
	@echo "Infrastructure Commands:"
	@echo "  make up          Start the full EFIDP Docker stack"
	@echo "  make down        Stop and remove containers (keep volumes)"
	@echo "  make down-v      Stop containers and remove all volumes"
	@echo "  make restart     Restart all containers"
	@echo "  make build       Build custom Docker images (FastAPI)"
	@echo "  make logs        Follow logs from all services"
	@echo "  make ps          Show running container status"
	@echo "  make health      Run health check against all service endpoints"
	@echo ""

# ── Developer Tooling ─────────────────────────────────────────────────────────

install:
	pip install --upgrade pip
	pip install -e ".[dev,api]"
	pre-commit install

lint:
	ruff check .

format:
	ruff format --check .

format-fix:
	ruff format .
	ruff check --fix .

typecheck:
	mypy src tests

test:
	pytest tests

test-cov:
	pytest --cov=src/efidp --cov-report=term-missing --cov-report=html

check: lint format typecheck test-cov

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

# ── Infrastructure (Docker Compose) ──────────────────────────────────────────

up:
	cp -n .env.example .env 2>/dev/null || true
	$(COMPOSE) up -d --wait
	@echo ""
	@echo "EFIDP Stack is running. Services available at:"
	@echo "  PostgreSQL  → localhost:5433"
	@echo "  MinIO API   → http://localhost:9000"
	@echo "  MinIO UI    → http://localhost:9001"
	@echo "  Kafka       → localhost:9092"
	@echo "  Redis       → localhost:6380"
	@echo "  Airflow     → http://localhost:8085"
	@echo "  FastAPI     → http://localhost:8001/docs"
	@echo "  Prometheus  → http://localhost:9090"
	@echo "  Grafana     → http://localhost:3001"

down:
	$(COMPOSE) down

down-v:
	$(COMPOSE) down -v

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build efidp-api

logs:
	$(COMPOSE) logs -f

logs-%:
	$(COMPOSE) logs -f efidp-$*

ps:
	$(COMPOSE) ps

health:
	@echo "Checking EFIDP service health..."
	@curl -sf http://localhost:9000/minio/health/live > /dev/null && echo "  MinIO       HEALTHY" || echo "  MinIO       UNHEALTHY"
	@curl -sf http://localhost:9090/-/healthy > /dev/null && echo "  Prometheus  HEALTHY" || echo "  Prometheus  UNHEALTHY"
	@curl -sf http://localhost:3001/api/health > /dev/null && echo "  Grafana     HEALTHY" || echo "  Grafana     UNHEALTHY"
	@curl -sf http://localhost:8001/api/v1/health > /dev/null && echo "  FastAPI     HEALTHY" || echo "  FastAPI     UNHEALTHY"
	@curl -sf http://localhost:8085/health > /dev/null && echo "  Airflow     HEALTHY" || echo "  Airflow     UNHEALTHY"
