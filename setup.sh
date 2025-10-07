#!/bin/bash
# Setup script for Finance AI Dashboard with Agent Workflow

set -e

echo "🚀 Finance AI Dashboard - Agent Workflow Setup"
echo "=============================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install base requirements
echo "📥 Installing base dependencies..."
pip install --upgrade pip
pip install dash pandas plotly pdfplumber pytesseract Pillow

# Detect OS and install llama-cpp-python with appropriate flags
echo ""
echo "🤖 Installing LLM dependencies..."
echo "Detecting system architecture..."

OS=$(uname -s)
ARCH=$(uname -m)

if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
        echo "✓ Detected: macOS Apple Silicon"
        echo "Installing llama-cpp-python with Metal support..."
        CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python==0.2.90
    else
        echo "✓ Detected: macOS Intel"
        echo "Installing llama-cpp-python..."
        pip install llama-cpp-python==0.2.90
    fi
elif [ "$OS" = "Linux" ]; then
    echo "✓ Detected: Linux"
    echo "Installing llama-cpp-python..."
    # Check for CUDA
    if command -v nvidia-smi &> /dev/null; then
        echo "CUDA detected. Installing with CUDA support..."
        CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python==0.2.90
    else
        echo "Installing CPU-only version..."
        pip install llama-cpp-python==0.2.90
    fi
else
    echo "✓ Detected: $OS"
    echo "Installing llama-cpp-python..."
    pip install llama-cpp-python==0.2.90
fi

# Check for model file
echo ""
echo "🔍 Checking for LLM model file..."
MODEL_FILE="mistral-7b-instruct-v0.1.Q5_0.gguf"

if [ -f "$MODEL_FILE" ]; then
    echo "✓ Model file found: $MODEL_FILE"
    MODEL_SIZE=$(du -h "$MODEL_FILE" | awk '{print $1}')
    echo "  Size: $MODEL_SIZE"
else
    echo "⚠️  Model file not found: $MODEL_FILE"
    echo ""
    echo "Please download the model file manually:"
    echo "  wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf"
    echo ""
    echo "Or using curl:"
    echo "  curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf"
    echo ""
    echo "The app will work without the model but won't use intelligent agent workflow."
fi

# Create necessary directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/uploads
mkdir -p data/temp
echo "✓ Directories created"

# Check for Tesseract (optional)
echo ""
echo "🔍 Checking for Tesseract OCR (optional)..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo "✓ $TESSERACT_VERSION"
else
    echo "⚠️  Tesseract not found (optional for PDF OCR)"
    if [ "$OS" = "Darwin" ]; then
        echo "  Install with: brew install tesseract"
    elif [ "$OS" = "Linux" ]; then
        echo "  Install with: sudo apt-get install tesseract-ocr"
    fi
fi

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  source .venv/bin/activate"
echo "  python -m finance_ai"
echo ""
echo "The app will be available at: http://127.0.0.1:8050"
echo ""
echo "For more information on the agent workflow:"
echo "  cat AGENT_WORKFLOW.md"
echo "=============================================="
