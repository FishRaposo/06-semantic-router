.PHONY: help install test lint format clean dev dev-down seed setup

help:
	@echo "SemanticRouter - Available targets:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run ruff + mypy"
	@echo "  format      Run ruff format"
	@echo "  clean       Remove build artifacts"
	@echo "  dev         Start docker compose"
	@echo "  dev-down    Stop docker compose"
	@echo "  seed        Load routes from sample config"
	@echo "  setup       First-time setup"

install:
	pip install -e ".[dev]"
	cd dashboard && npm ci

test:
	python -m pytest tests/ -v --cov=semantic_router --cov-report=term-missing

lint:
	ruff check semantic_router/ tests/ && mypy semantic_router

format:
	ruff format semantic_router/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf dashboard/.next
	rm -rf .coverage htmlcov/

dev:
	docker compose up -d

dev-down:
	docker compose down

seed:
	@echo "Routes are loaded from config/routes.yaml at startup."
	@echo "Use 'POST /api/v1/routes' to add routes manually."


setup: install dev seed
