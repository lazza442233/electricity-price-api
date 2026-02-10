.PHONY: install run test lint format clean help

.DEFAULT_GOAL := help

install:
	pip install -r requirements-dev.txt

run:
	flask run --debug

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

test-fast:
	pytest tests/ -v

lint:
	ruff check app/ tests/
	ruff format --check app/ tests/
	mypy app/

format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^## //p' $(MAKEFILE_LIST) | column -t -s ':'
