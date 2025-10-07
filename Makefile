PY := python3

.PHONY: install run preflight test

install:
	poetry install

run:
	poetry run finance-ai

preflight:
	poetry run $(PY) preflight_check.py

test:
	poetry run $(PY) test_installation.py
