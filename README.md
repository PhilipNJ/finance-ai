# Finance AI Dashboard 🤖# Finance AI Dashboard 🤖💰



**AI-Powered Personal Finance Management** | 100% Offline | Privacy-FirstAn **AI-first** offline personal finance dashboard powered by local LLMs. Upload bank statements, credit card bills, or any financial documents, and let intelligent agents extract, organize, and analyze your data automatically.



An intelligent personal finance dashboard that uses local AI agents to automatically extract, organize, and analyze your financial data from any document format.## 🌟 Features



[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)### AI-Powered Multi-Agent Workflow

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)This app uses **three intelligent AI agents** working together:

[![AI-First](https://img.shields.io/badge/AI-First-purple.svg)](docs/ai-architecture.md)

- **🔍 Agent 1 (Extractor)**: Reads and understands any financial document using Mistral-7B LLM

## 🌟 Features- **📊 Agent 2 (Organizer)**: Intelligently categorizes and structures your data

- **💾 Agent 3 (Database Expert)**: Automatically evolves database schema as needed

- **🤖 Multi-Agent AI System**: Three intelligent agents work together to process your data

- **📄 Universal File Support**: Upload CSV, PDF, or text files - even handwritten receipts (OCR)### Core Capabilities

- **🧠 Context-Aware Processing**: LLM understands your documents, not just pattern matching- 📄 **Universal file support**: CSV, PDF, text - even unstructured documents

- **🔄 Dynamic Schema**: Database evolves automatically with new data types- 🧠 **Intelligent extraction**: LLM understands context, not just patterns

- **📊 Interactive Dashboard**: Beautiful visualizations of your spending patterns- 🔄 **Dynamic schema evolution**: Database adapts to new data types automatically

- **🔒 100% Offline**: No cloud APIs, complete privacy- 📈 **Visual dashboard**: Interactive charts for spending analysis

- ✏️ **Editable categories**: Manual corrections improve AI learning

## 🚀 Quick Start- 🔒 **100% offline**: No cloud, no external APIs, complete privacy



### Prerequisites## 🛠️ Tech Stack

- Python 3.10 or higher- **AI Engine**: llama-cpp-python + Mistral-7B-Instruct (local LLM)

- 8GB RAM minimum- **Framework**: Python, Dash, Plotly

- ~5GB free disk space- **Database**: SQLite with dynamic schema evolution

- **Parsing**: pandas, pdfplumber, OCR support (Tesseract)

### Installation

## Prereqs (macOS)

```bash- Python 3.10+

# 1. Clone the repository- For PDF OCR fallback, install Tesseract:

git clone https://github.com/PhilipNJ/finance-ai.git  - `brew install tesseract`

cd finance-ai

## 🚀 Quick Start

# 2. Run automated setup

./setup.sh### Automated Setup (Recommended)

```bash

# 3. Start the application./setup.sh

python3 app.py```

```

This script will:

Open your browser to **http://127.0.0.1:8050**- ✅ Create virtual environment

- ✅ Install all dependencies (including LLM support)

### Manual Installation- ✅ Check for the AI model file

- ✅ Verify Tesseract OCR (optional)

<details>

<summary>Click to expand manual installation steps</summary>### Manual Setup



```bash#### 1. Create Virtual Environment

# Create virtual environment```bash

python3 -m venv .venvpython3 -m venv .venv

source .venv/bin/activatesource .venv/bin/activate

```

# Install dependencies

pip install dash pandas plotly pdfplumber pytesseract Pillow#### 2. Install Dependencies



# Install LLM support (macOS Apple Silicon)**macOS (Apple Silicon)**

CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python```bash

pip install dash pandas plotly pdfplumber pytesseract Pillow

# Download AI model (~4.7GB)CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90

wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf```



# Run the app**macOS (Intel) / Linux / Windows**

python3 app.py```bash

```pip install -r requirements.txt

```

</details>

#### 3. Download AI Model (~4.2GB)

## 📖 How It Works

**Required**: This app needs the Mistral-7B model to function.

```mermaid

graph LR```bash

    A[Upload File] --> B[Agent 1: Extractor]# Using wget

    B --> C[Agent 2: Organizer]wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf

    C --> D[Agent 3: DB Expert]

    D --> E[Dashboard]# Or using curl

    curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf \

    style B fill:#e1f5ff  https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf

    style C fill:#e8f5e9```

    style D fill:#fff3e0

#### 4. Run the App

Using Poetry:

```bash
poetry install
poetry run python app.py
```

Or, after install:

```bash
poetry run finance-ai
```

Open your browser to: **http://127.0.0.1:8050**



[Learn more about the AI architecture →](docs/ai-architecture.md)### Testing Your Setup

```bash

## 🎯 Use Casespython test_installation.py

```

- **Bank Statements**: Automatically extract and categorize transactions

- **Credit Card Bills**: Parse PDFs into structured dataThis will verify:

- **Invoices & Receipts**: Extract details from unstructured documents- ✓ All dependencies installed

- **Budget Planning**: Upload budget spreadsheets for tracking- ✓ LLM model file present

- **Financial Reports**: Analyze spending patterns over time- ✓ Agents working correctly



## 🛠️ Tech Stack## 💡 How It Works



| Component | Technology |1. **Upload** any financial document (CSV, PDF, text)

|-----------|-----------|2. **Agent 1** reads and understands the document using AI

| **AI Engine** | Mistral-7B-Instruct (local LLM) |3. **Agent 2** intelligently organizes the data by type

| **Framework** | Python, Dash, Plotly |4. **Agent 3** creates/updates database tables automatically

| **Database** | SQLite with dynamic schema |5. **View** your data in beautiful interactive dashboards

| **Parsing** | pandas, pdfplumber, OCR |

| **LLM Runtime** | llama-cpp-python |**No manual data entry. No configuration. Just upload and go.** 🎯



## 📚 Documentation## 📋 System Requirements



- **[Getting Started](docs/getting-started.md)** - Installation and first steps- **Python**: 3.10 or higher

- **[AI Architecture](docs/ai-architecture.md)** - How the AI agents work- **RAM**: 8GB minimum (for LLM model)

- **[Agent Workflow](docs/agent-workflow.md)** - Technical deep dive- **Storage**: ~5GB (4.2GB for model + data)

- **[Troubleshooting](docs/troubleshooting.md)** - Common issues- **OS**: macOS, Linux, or Windows



[📖 View Full Documentation](https://philipnj.github.io/finance-ai/)## 📁 Project Structure



## 🔧 Quick Configuration```

finance-ai/

```bash├── app.py                    # Main Dash application

# Run pre-flight check├── agents.py                 # AI agent system (3 agents)

python3 preflight_check.py├── llm_handler.py           # LLM interface

├── finance_db.py            # Database operations

# Test installation├── parsers.py               # File parsers

python3 test_installation.py├── utils.py                 # Utilities

```├── setup.sh                 # Automated setup

├── test_installation.py     # Setup verification

See [Configuration Guide](docs/configuration.md) for advanced options.├── mistral-7b-*.gguf       # AI model file

├── data/

## 🤝 Contributing│   ├── finance.db          # SQLite database (auto-created)

│   ├── uploads/            # Uploaded files

Contributions welcome! Focus areas:│   └── temp/               # Temporary processing files

- 🎯 New data types (investments, loans, crypto)├── assets/

- 🧠 Better LLM prompts│   └── style.css           # Dashboard styling

- 📊 New visualizations└── docs/

    ├── AGENT_WORKFLOW.md    # Detailed workflow docs

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.    └── ARCHITECTURE_DIAGRAM.md

```

## 📋 System Requirements

## 🎯 What Makes This Special

| Requirement | Minimum | Recommended |

|-------------|---------|-------------|- **🧠 AI-First Design**: Built around LLM capabilities from the ground up

| Python | 3.10+ | 3.11+ |- **🔄 Self-Adapting**: Database schema evolves with your data

| RAM | 8GB | 16GB |- **🎨 Universal Parser**: Handles structured AND unstructured documents

| Storage | 5GB | 10GB |- **🔒 Privacy-First**: Everything runs locally, zero cloud dependencies

- **⚡ Production-Ready**: Error handling, logging, cleanup built-in

## 🔒 Privacy

## 📖 Documentation

- ✅ 100% Offline - No external API calls

- ✅ Local Processing - Data never leaves your machine- **[AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)** - Deep dive into the AI agent system

- ✅ No Telemetry - Zero tracking- **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - Visual architecture diagrams

- ✅ Open Source - Audit the code yourself- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details



## 📝 License## 🤝 Contributing



MIT License - see [LICENSE](LICENSE) file for details.This is an AI-first financial dashboard. Key areas for contribution:

- Support for more document types

---- Additional data types (investments, loans, budgets)

- Enhanced LLM prompts

**Made with 🤖 and ❤️**- Better visualization options



[⭐ Star this repo](https://github.com/PhilipNJ/finance-ai) if you find it useful!## ⚠️ Important Notes


- **LLM Required**: This app requires `llama-cpp-python` and the Mistral model to function
- **First Run**: Model loading takes 5-10 seconds on first upload
- **Offline Only**: No external API calls, completely private
- **Auto-Cleanup**: Temporary files are automatically deleted after processing
