# ALETHEIA-LATTICE
.DEFAULT_GOAL := help
.PHONY: help install test lint full clean

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

lint:
	ruff check aletheia_lattice/ tests/

full: lint test

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist build *.egg-info .pytest_cache .coverage htmlcov

help:
	@echo "install  |  test  |  lint  |  full  |  clean"
