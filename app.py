"""Compat launcher for Finance AI.

Prefer running:
  - `python -m finance_ai`
  - or `poetry run finance-ai`

This file delegates to the package entrypoint for backward compatibility.
"""
from finance_ai.app import main


if __name__ == "__main__":
    main()
