# Getting Started

This guide will help you install and run Finance AI Dashboard on your system.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **8GB RAM minimum** (16GB recommended for better performance)
- **~5GB free disk space** for the AI model and dependencies
- **Terminal/Command Line** access

!!! info "Supported Platforms"
    Finance AI works on macOS, Linux, and Windows. Installation steps may vary slightly.

## Installation Methods

=== "Automated (Recommended)"

    The easiest way to install Finance AI is using the automated setup script:

    ```bash
    # 1. Clone the repository
    git clone https://github.com/PhilipNJ/finance-ai.git
    cd finance-ai

    # 2. Run setup script
    ./setup.sh
    ```

    The script will:
    - ✅ Create a virtual environment
    - ✅ Install all Python dependencies
    - ✅ Install llama-cpp-python with correct flags for your system
    - ✅ Check for the AI model file
    - ✅ Verify Tesseract OCR (optional)

=== "Manual"

    ### Step 1: Create Virtual Environment

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

    ### Step 2: Install Base Dependencies

    ```bash
    pip install --upgrade pip
    pip install dash pandas plotly pdfplumber pytesseract Pillow
    ```

    ### Step 3: Install LLM Support

    **macOS (Apple Silicon):**
    ```bash
    CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90
    ```

    **macOS (Intel):**
    ```bash
    pip install llama-cpp-python==0.2.90
    ```

    **Linux (with CUDA):**
    ```bash
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python==0.2.90
    ```

    **Linux (CPU only):**
    ```bash
    pip install llama-cpp-python==0.2.90
    ```

    **Windows:**
    ```bash
    pip install llama-cpp-python==0.2.90
    ```

    ### Step 4: Download AI Model

    Download the Mistral-7B model (~4.7GB):

    ```bash
    # Using wget
    wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf

    # Or using curl
    curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf \
      https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf
    ```

=== "From Requirements (exported)"

    If you prefer using `requirements.txt`, export it from Poetry first:

    ```bash
    # 1. Clone and navigate
    git clone https://github.com/PhilipNJ/finance-ai.git
    cd finance-ai

    # 2. Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # 3. Export and install requirements
    make export-reqs
    pip install -r requirements.txt

    # 4. Install llama-cpp-python separately with system-specific flags
    # (See Manual tab for your system)

    # 5. Download AI model (see Manual tab)
    ```

## Verification

### Pre-Flight Check

Run the pre-flight check to verify everything is installed correctly:

```bash
poetry run python scripts/preflight_check.py
```

Expected output:

```
======================================================================
🤖 Finance AI Dashboard - Pre-Flight Check
======================================================================
Checking AI Dependencies...
----------------------------------------------------------------------
✅ llama-cpp-python installed
✅ AI model found: mistral-7b-instruct-v0.1.Q5_0.gguf (4766.2 MB)

Checking Other Dependencies...
----------------------------------------------------------------------
✅ dash (Dash framework)
✅ pandas (Data processing)
✅ plotly (Visualization)
✅ pdfplumber (PDF parsing)

Checking Directories...
----------------------------------------------------------------------
✅ Directory exists: data
✅ Directory exists: data/uploads
✅ Directory exists: data/temp

======================================================================
✅ ALL CHECKS PASSED - Ready to launch!
======================================================================
```

### Installation Test

Run the full installation test suite:

```bash
python3 test_installation.py
```

This will test:
- ✅ All imports work correctly
- ✅ AI model file is present and valid
- ✅ Agent modules load successfully
- ✅ Database connection works
- ✅ Sample extraction functions

## Running the Application

### Start the App

```bash
python3 app.py
```

Expected startup output:

```
======================================================================
🤖 Finance AI Dashboard - Starting Up
======================================================================
✅ LLM dependencies available
🔧 Initializing AI agent workflow...
🤖 Initializing AI engine with mistral-7b-instruct-v0.1.Q5_0.gguf...
Loading LLM from mistral-7b-instruct-v0.1.Q5_0.gguf...
LLM loaded successfully.
✅ AI agents ready!
======================================================================
✅ Finance AI Dashboard ready!
======================================================================

Dash is running on http://127.0.0.1:8050/
```

### Access the Dashboard

Open your browser and navigate to:

```
http://127.0.0.1:8050
```

You should see the Finance AI Dashboard home screen with the upload interface.

## Optional: Tesseract OCR

For OCR support (reading scanned PDFs and images):

=== "macOS"
    ```bash
    brew install tesseract
    ```

=== "Ubuntu/Debian"
    ```bash
    sudo apt-get update
    sudo apt-get install tesseract-ocr
    ```

=== "Windows"
    Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Troubleshooting

### Common Issues

!!! failure "llama-cpp-python installation fails"
    **Problem**: Build errors when installing llama-cpp-python
    
    **Solutions**:
    
    1. Install build tools:
        ```bash
        # macOS
        xcode-select --install
        
        # Ubuntu/Debian
        sudo apt-get install build-essential
        ```
    
    2. Use pre-built wheels:
        ```bash
        pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
        ```

!!! failure "Model file not found"
    **Problem**: `Model file not found at mistral-7b-instruct-v0.1.Q5_0.gguf`
    
    **Solution**: Download the model file (see Installation Step 4 above)

!!! failure "Out of memory"
    **Problem**: System runs out of RAM when loading model
    
    **Solutions**:
    
    1. Use a smaller model (Q4 quantization):
        ```bash
        wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf
        ```
    
    2. Adjust context window in `llm_handler.py`:
        ```python
        LLMHandler(n_ctx=2048)  # Reduce from default 4096
        ```

!!! failure "Import errors"
    **Problem**: `ModuleNotFoundError` when running the app
    
    **Solution**: Activate virtual environment first:
    ```bash
    source .venv/bin/activate  # macOS/Linux
    .venv\Scripts\activate      # Windows
    ```

For more issues, see the [Troubleshooting Guide](troubleshooting.md).

## Next Steps

Now that you have Finance AI installed and running:

1. **[Quick Start Guide](quick-start.md)** - Upload your first document
2. **[Dashboard Guide](user-guide/dashboard.md)** - Explore the interface
3. **[AI Architecture](ai-architecture.md)** - Understand how it works

---

!!! tip "Performance Tip"
    On first run, the AI model takes 5-10 seconds to load. Subsequent uploads are much faster (2-5 seconds) as the model stays in memory.
