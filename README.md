# Finance AI Dashboard 🤖

AI-first, offline personal finance dashboard powered by a local multi-agent workflow. Drop in CSV, PDF, or text statements and let agents extract, organize, and visualize your finances. 100% local, privacy-first.

Badges: Python 3.10+, MIT

## Features

- 🤖 Multi-agent AI system: Extractor, Organizer, DB Expert
- 🔄 Dynamic schema: SQLite evolves to fit new fields
- 📦 Pure Python, Dash UI, SQLite storage
- 🧠 Optional local LLM via Ollama

## Quickstart

1) Install dependencies (Poetry is the source of truth)

	 - With Poetry:
		 - Install: `poetry install`
		 - Run preflight check: `poetry run python scripts/preflight_check.py`
		 - Launch app: `poetry run finance-ai`

	 - With venv + pip (via export):
		 - Generate requirements.txt: `make export-reqs`
		 - Create/activate venv, then: `pip install -r requirements.txt`
		 - Launch app: `python -m finance_ai`

2) Add files

- Put sample CSV/PDF/TXT files in `test_files/` and (re)start the app. New files are auto-processed on startup and de-duplicated using hashes stored in `data/processed_files.json`.

3) Where data lives

- SQLite DB: `data/finance.db`
- Temp + outputs: `data/temp/`
- Processed tracker: `data/processed_files.json`

## Development

- Make targets: `make install`, `make run`, `make preflight`, `make test`, `make export-reqs`
- Module entry point: `python -m finance_ai` or `poetry run finance-ai`

## Notes

- LLM features are optional. If Ollama isn’t running, the app still works with baseline extraction.

