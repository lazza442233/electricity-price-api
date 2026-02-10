.PHONY: install run prod test lint format clean help

.DEFAULT_GOAL := help

## install: Install all dependencies
install:
	pip install -r requirements-dev.txt

## run: Start development server
run:
	flask run --debug

## prod: Run with gunicorn (production)
prod:
	FLASK_ENV=production gunicorn "app:create_app()" --bind 0.0.0.0:5000

## test: Run tests with coverage
test:
	pytest tests/ -v --cov=app --cov-report=term-missing

## test-fast: Run tests without coverage
test-fast:
	pytest tests/ -v

## lint: Check code style
lint:
	ruff check app/ tests/
	ruff format --check app/ tests/
	mypy app/

## format: Auto-format code
format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

## clean: Remove cache files
clean:
	rm -rf __pycache__ **/__pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage

## help: Show this help message
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^## //p' $(MAKEFILE_LIST) | column -t -s ':'
