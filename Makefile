PY := python3

.PHONY: install run preflight test

install:
	poetry install

run:
	poetry run finance-ai

preflight:
	poetry run $(PY) scripts/preflight_check.py

test:
	poetry run $(PY) scripts/test_installation.py
