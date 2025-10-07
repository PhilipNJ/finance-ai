PY := python3

.PHONY: install run preflight test export-reqs

install:
	poetry install

run:
	poetry run finance-ai

preflight:
	poetry run $(PY) scripts/preflight_check.py

test:
	poetry run $(PY) scripts/test_installation.py

export-reqs:
	poetry export --format=requirements.txt --output=requirements.txt --without-hashes
