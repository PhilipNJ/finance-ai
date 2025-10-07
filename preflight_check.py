#!/usr/bin/env python3
"""
Pre-flight check for Finance AI Dashboard.
Verifies that all AI dependencies are available before starting the app.
"""
import sys
from pathlib import Path


def check_llm_library():
    """Check if llama-cpp-python is installed."""
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python installed")
        return True
    except ImportError:
        print("\n" + "="*70)
        print("❌ ERROR: llama-cpp-python is NOT installed")
        print("="*70)
        print("\nThis AI-powered dashboard requires LLM capabilities.")
        print("\nInstallation:")
        print("\n  macOS (Apple Silicon):")
        print("    CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python")
        print("\n  Other systems:")
        print("    pip install llama-cpp-python")
        print("\n  Or run the setup script:")
        print("    ./setup.sh")
        print("\n" + "="*70 + "\n")
        return False


def check_model_file():
    """Check if the AI model file exists."""
    model_path = Path("mistral-7b-instruct-v0.1.Q5_0.gguf")
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ AI model found: {model_path.name} ({size_mb:.1f} MB)")
        return True
    else:
        print("\n" + "="*70)
        print(f"❌ ERROR: AI model file not found")
        print("="*70)
        print(f"\nExpected location: {model_path.absolute()}")
        print("\nDownload the Mistral-7B model (~4.2GB):")
        print("\n  Using wget:")
        print("    wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf")
        print("\n  Using curl:")
        print("    curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf \\")
        print("      https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf")
        print("\n" + "="*70 + "\n")
        return False


def check_other_dependencies():
    """Check other required dependencies."""
    required = {
        'dash': 'Dash framework',
        'pandas': 'Data processing',
        'plotly': 'Visualization',
        'pdfplumber': 'PDF parsing'
    }
    
    all_ok = True
    for module, desc in required.items():
        try:
            __import__(module)
            print(f"✅ {module} ({desc})")
        except ImportError:
            print(f"❌ {module} NOT installed ({desc})")
            all_ok = False
    
    return all_ok


def check_directories():
    """Check that required directories exist."""
    dirs = ['data', 'data/uploads', 'data/temp']
    
    for dir_path in dirs:
        path = Path(dir_path)
        if not path.exists():
            print(f"📁 Creating directory: {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"✅ Directory exists: {dir_path}")
    
    return True


def main():
    """Run all pre-flight checks."""
    print("\n" + "="*70)
    print("🤖 Finance AI Dashboard - Pre-Flight Check")
    print("="*70 + "\n")
    
    print("Checking AI Dependencies...")
    print("-" * 70)
    llm_ok = check_llm_library()
    model_ok = check_model_file()
    
    print("\nChecking Other Dependencies...")
    print("-" * 70)
    deps_ok = check_other_dependencies()
    
    print("\nChecking Directories...")
    print("-" * 70)
    dirs_ok = check_directories()
    
    print("\n" + "="*70)
    
    if llm_ok and model_ok and deps_ok and dirs_ok:
        print("✅ ALL CHECKS PASSED - Ready to launch!")
        print("="*70)
        print("\nStart the app with:")
        print("  python app.py")
        print("\nThen open: http://127.0.0.1:8050")
        print("="*70 + "\n")
        return 0
    else:
        print("❌ CHECKS FAILED - Please fix the issues above")
        print("="*70)
        print("\nQuick fix:")
        print("  ./setup.sh")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
