# Local Personal Finance Dashboard (Offline)

A small offline Dash app to ingest bank/credit card/loan statements (CSV/PDF), parse transactions, categorize via simple rules, and present a minimal dashboard.

## Features (MVP)
- Upload CSV or PDF files
- Parse to transactions and save in SQLite `./data/finance.db`
- Editable categories with simple keyword memory (`mem_labels`)
- Dashboard: totals, spend by category (pie), monthly cashflow (line)

## Stack
- Python, Dash, Plotly
- SQLite (sqlite3 stdlib)
- Parsing: pandas, pdfplumber (with optional Tesseract OCR fallback)

## Prereqs (macOS)
- Python 3.10+
- For PDF OCR fallback, install Tesseract:
  - `brew install tesseract`

## Setup
1. Create and activate a virtual environment (recommended).
2. Install Python packages.
3. Run the app.

### Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app starts on http://127.0.0.1:8050 (no external network calls).

## Notes
- Uploaded files are saved under `./data/uploads/` with a unique name.
- DB schema is created on first run.
- Future: local LLM categorization (llama.cpp/GPT4All), embeddings + FAISS.
