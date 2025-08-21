.PHONY: help install install-dev test test-cov lint format clean build upload dev-setup example check release

help:  ## Show this help message
	@echo "MCP Merge Request Summarizer - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start: make install && make example"

install:  ## Install the package in development mode
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,test]"
	pre-commit install

test:  ## Run tests
	python -m pytest tests/ -v

test-cov:  ## Run tests with coverage
	python -m pytest tests/ --cov=mcp_mr_summarizer --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format:  ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

clean:  ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package for distribution
	python -m build

upload:  ## Upload to PyPI (requires authentication)
	python -m twine upload dist/*

upload-test:  ## Upload to Test PyPI
	python -m twine upload --repository testpypi dist/*

dev-setup:  ## Set up complete development environment
	python -m venv venv
	. venv/bin/activate && pip install -e ".[dev,test]"
	. venv/bin/activate && pre-commit install
	@echo "Development environment set up. Activate with: source venv/bin/activate"

example:  ## Run example usage to test installation
	python -m mcp_mr_summarizer.cli --help

check:  ## Run all checks (lint, test, format check)
	@echo "Running all checks..."
	@make lint
	@make test
	@echo "All checks passed!"

release:  ## Prepare a new release (clean, build, test)
	@echo "Preparing release..."
	@make clean
	@make test
	@make build
	@echo "Release ready! Run 'make upload' to publish to PyPI"
