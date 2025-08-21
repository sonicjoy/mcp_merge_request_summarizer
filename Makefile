.PHONY: help install install-dev test test-cov lint format clean build upload

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,test]"
	pre-commit install

test:  ## Run tests
	python -m pytest tests/ -v

test-cov:  ## Run tests with coverage
	python -m pytest tests/ --cov=mcp_mr_summarizer --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format:  ## Format code
	black src/ tests/
	isort src/ tests/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

upload:  ## Upload to PyPI (requires authentication)
	python -m twine upload dist/*

upload-test:  ## Upload to Test PyPI
	python -m twine upload --repository testpypi dist/*

dev-setup:  ## Set up development environment
	python -m venv venv
	. venv/bin/activate && pip install -e ".[dev,test]"
	. venv/bin/activate && pre-commit install
	@echo "Development environment set up. Activate with: source venv/bin/activate"

example:  ## Run example usage
	mcp-mr-summarizer --help
