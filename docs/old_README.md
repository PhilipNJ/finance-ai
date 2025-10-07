# Finance AI Dashboard 🤖💰

An **AI-first** offline personal finance dashboard powered by local LLMs. Upload bank statements, credit card bills, or any financial documents, and let intelligent agents extract, organize, and analyze your data automatically.

## 🌟 Features

### AI-Powered Multi-Agent Workflow
This app uses **three intelligent AI agents** working together:

- **🔍 Agent 1 (Extractor)**: Reads and understands any financial document using Mistral-7B LLM
- **📊 Agent 2 (Organizer)**: Intelligently categorizes and structures your data
- **💾 Agent 3 (Database Expert)**: Automatically evolves database schema as needed

### Core Capabilities
- 📄 **Universal file support**: CSV, PDF, text - even unstructured documents
- 🧠 **Intelligent extraction**: LLM understands context, not just patterns
- 🔄 **Dynamic schema evolution**: Database adapts to new data types automatically
- 📈 **Visual dashboard**: Interactive charts for spending analysis
- ✏️ **Editable categories**: Manual corrections improve AI learning
- 🔒 **100% offline**: No cloud, no external APIs, complete privacy

## 🛠️ Tech Stack
- **AI Engine**: llama-cpp-python + Mistral-7B-Instruct (local LLM)
- **Framework**: Python, Dash, Plotly
- **Database**: SQLite with dynamic schema evolution
- **Parsing**: pandas, pdfplumber, OCR support (Tesseract)

## Prereqs (macOS)
- Python 3.10+
- For PDF OCR fallback, install Tesseract:
  - `brew install tesseract`

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
./setup.sh
```

This script will:
- ✅ Create virtual environment
- ✅ Install all dependencies (including LLM support)
- ✅ Check for the AI model file
- ✅ Verify Tesseract OCR (optional)

### Manual Setup

#### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Dependencies

**macOS (Apple Silicon)**
```bash
pip install dash pandas plotly pdfplumber pytesseract Pillow
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90
```

**macOS (Intel) / Linux / Windows**
```bash
pip install -r requirements.txt
```

#### 3. Download AI Model (~4.2GB)

**Required**: This app needs the Mistral-7B model to function.

```bash
# Using wget
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf

# Or using curl
curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf \
  https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf
```

#### 4. Run the App
```bash
python app.py
```

Open your browser to: **http://127.0.0.1:8050**

### Testing Your Setup
```bash
python test_installation.py
```

This will verify:
- ✓ All dependencies installed
- ✓ LLM model file present
- ✓ Agents working correctly

## 💡 How It Works

1. **Upload** any financial document (CSV, PDF, text)
2. **Agent 1** reads and understands the document using AI
3. **Agent 2** intelligently organizes the data by type
4. **Agent 3** creates/updates database tables automatically
5. **View** your data in beautiful interactive dashboards

**No manual data entry. No configuration. Just upload and go.** 🎯

## 📋 System Requirements

- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (for LLM model)
- **Storage**: ~5GB (4.2GB for model + data)
- **OS**: macOS, Linux, or Windows

## 📁 Project Structure

```
finance-ai/
├── app.py                    # Main Dash application
├── agents.py                 # AI agent system (3 agents)
├── llm_handler.py           # LLM interface
├── finance_db.py            # Database operations
├── parsers.py               # File parsers
├── utils.py                 # Utilities
├── setup.sh                 # Automated setup
├── test_installation.py     # Setup verification
├── mistral-7b-*.gguf       # AI model file
├── data/
│   ├── finance.db          # SQLite database (auto-created)
│   ├── uploads/            # Uploaded files
│   └── temp/               # Temporary processing files
├── assets/
│   └── style.css           # Dashboard styling
└── docs/
    ├── AGENT_WORKFLOW.md    # Detailed workflow docs
    └── ARCHITECTURE_DIAGRAM.md
```

## 🎯 What Makes This Special

- **🧠 AI-First Design**: Built around LLM capabilities from the ground up
- **🔄 Self-Adapting**: Database schema evolves with your data
- **🎨 Universal Parser**: Handles structured AND unstructured documents
- **🔒 Privacy-First**: Everything runs locally, zero cloud dependencies
- **⚡ Production-Ready**: Error handling, logging, cleanup built-in

## 📖 Documentation

- **[AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)** - Deep dive into the AI agent system
- **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - Visual architecture diagrams
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## 🤝 Contributing

This is an AI-first financial dashboard. Key areas for contribution:
- Support for more document types
- Additional data types (investments, loans, budgets)
- Enhanced LLM prompts
- Better visualization options

## ⚠️ Important Notes

- **LLM Required**: This app requires `llama-cpp-python` and the Mistral model to function
- **First Run**: Model loading takes 5-10 seconds on first upload
- **Offline Only**: No external API calls, completely private
- **Auto-Cleanup**: Temporary files are automatically deleted after processing
