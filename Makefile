.PHONY: help install lint format typecheck test test-cov check clean

help:
	@echo "Available commands:"
	@echo "  make install     Install project and development dependencies"
	@echo "  make lint        Run ruff linter check"
	@echo "  make format      Run ruff formatting check"
	@echo "  make typecheck   Run static type checking with mypy"
	@echo "  make test        Run unit tests"
	@echo "  make test-cov    Run unit tests with coverage reporting"
	@echo "  make check       Run all linting, formatting, type checking, and tests"
	@echo "  make clean       Clean build, cache, and coverage artifacts"

install:
	pip install --upgrade pip
	pip install -e ".[dev]"
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
