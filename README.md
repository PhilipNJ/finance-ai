# Local Personal Finance Dashboard (Offline)

A smart offline Dash app to ingest bank/credit card/loan statements (CSV/PDF), parse transactions, categorize via AI agents, and present a minimal dashboard.

## Features

### Core Features
- Upload CSV, PDF, or text files
- **NEW**: Intelligent multi-agent workflow for data extraction and organization
- Parse to transactions and save in SQLite `./data/finance.db`
- Editable categories with simple keyword memory (`mem_labels`)
- Dashboard: totals, spend by category (pie), monthly cashflow (line)

### Agent Workflow (NEW! 🎉)
- **Agent 1**: Extracts all information from files using local LLM
- **Agent 2**: Organizes data into structured JSONs by type
- **Agent 3**: Dynamically creates database tables and writes data
- Automatic cleanup of temporary files
- Graceful fallback to classic parsing if LLM unavailable

## Stack
- Python, Dash, Plotly
- SQLite (sqlite3 stdlib)
- Parsing: pandas, pdfplumber (with optional Tesseract OCR fallback)
- **AI Agents**: llama-cpp-python with Mistral-7B-Instruct (local LLM)

## Prereqs (macOS)
- Python 3.10+
- For PDF OCR fallback, install Tesseract:
  - `brew install tesseract`

## Setup

### Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app starts on http://127.0.0.1:8050 (no external network calls).

### Agent Workflow Setup (Optional but Recommended)

For the intelligent agent workflow, you need to install `llama-cpp-python`:

#### macOS (Apple Silicon)
```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90
```

#### Other Systems
```bash
pip install llama-cpp-python==0.2.90
```

**Note**: The Mistral-7B-Instruct GGUF model file should be in the project root. If missing, it will be downloaded automatically on first run, or you can download manually from [Hugging Face](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF).

See **[AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)** for detailed setup and configuration.

## Usage

### With Agent Workflow (Intelligent)
Upload any CSV, PDF, or text file containing financial data. The agents will:
1. Extract all information intelligently
2. Identify and organize different data types
3. Create database tables as needed
4. Write structured data automatically

### Without Agent Workflow (Classic)
Set `USE_AGENT_WORKFLOW=false` to use the original parsing method:
```bash
export USE_AGENT_WORKFLOW=false
python app.py
```

## Notes
- Uploaded files are saved under `./data/uploads/` with a unique name
- Temporary agent files are stored in `./data/temp/` and auto-deleted after processing
- DB schema is created on first run and evolves dynamically with new data types
- The system gracefully falls back to classic parsing if LLM is unavailable
