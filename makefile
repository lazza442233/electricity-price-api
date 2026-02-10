.PHONY: install run test lint format clean help

.DEFAULT_GOAL := help

## install: Install all dependencies
install:
	pip install -r requirements-dev.txt

## run: Start development server
run:
	flask run --debug

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

## help: Show this help message
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^## //p' $(MAKEFILE_LIST) | column -t -s ':'
