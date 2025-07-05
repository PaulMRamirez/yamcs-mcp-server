.PHONY: help install install-dev clean test test-cov lint type-check format build docs serve-docs pre-commit

help:
	@echo "Available commands:"
	@echo "  make install       Install the package"
	@echo "  make install-dev   Install with development dependencies"
	@echo "  make clean         Clean build artifacts and caches"
	@echo "  make test          Run tests"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make lint          Run linting (ruff)"
	@echo "  make type-check    Run type checking (mypy)"
	@echo "  make format        Format code with ruff"
	@echo "  make build         Build distribution packages"
	@echo "  make docs          Build documentation"
	@echo "  make serve-docs    Serve documentation locally"
	@echo "  make pre-commit    Run pre-commit on all files"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"
	pre-commit install

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	pytest

test-cov:
	pytest --cov=yamcs_mcp --cov-report=term-missing --cov-report=html

lint:
	ruff check src tests
	ruff format --check src tests

type-check:
	mypy src

format:
	ruff check --fix src tests
	ruff format src tests

build: clean
	python -m build

docs:
	mkdocs build

serve-docs:
	mkdocs serve

pre-commit:
	pre-commit run --all-files