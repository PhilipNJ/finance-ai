#!/usr/bin/env python3
"""
Pre-flight check for Finance AI Dashboard.
Verifies that core dependencies and directories are available before starting the app.

Optional: checks connectivity to a local Ollama server for LLM features.
"""
import sys
from pathlib import Path


def check_ollama_connectivity():
    """Check if a local Ollama server is reachable (optional)."""
    try:
        import requests  # type: ignore
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.ok:
            print("✅ Ollama reachable at http://localhost:11434 (optional)")
            return True
        print("⚠️  Ollama not reachable (optional)")
        return False
    except Exception:
        print("⚠️  Ollama not reachable (optional)")
        return False


def check_model_file():
    """Deprecated: legacy local GGUF model (not required)."""
    model_path = Path("mistral-7b-instruct-v0.1.Q5_0.gguf")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"ℹ️  Legacy GGUF model present: {model_path.name} ({size_mb:.1f} MB) — not required")
    else:
        print("ℹ️  No local GGUF model found (not required)")
    return True


def check_other_dependencies():
    """Check other required dependencies."""
    required = {
        'dash': 'Dash framework',
        'pandas': 'Data processing',
        'plotly': 'Visualization',
    'pdfplumber': 'PDF parsing',
    'requests': 'HTTP (Ollama optional)'
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
    
    print("Checking Optional LLM Connectivity...")
    print("-" * 70)
    ollama_ok = check_ollama_connectivity()
    legacy_model_ok = check_model_file()
    
    print("\nChecking Other Dependencies...")
    print("-" * 70)
    deps_ok = check_other_dependencies()
    
    print("\nChecking Directories...")
    print("-" * 70)
    dirs_ok = check_directories()
    
    print("\n" + "="*70)
    
    if deps_ok and dirs_ok:
        print("✅ ALL CHECKS PASSED - Ready to launch!")
        print("="*70)
        print("\nStart the app with:")
        print("  poetry run finance-ai")
        print("\nThen open: http://127.0.0.1:8050")
        print("="*70 + "\n")
        return 0
    else:
        print("❌ CHECKS FAILED - Please fix the issues above")
        print("="*70)
        print("\nQuick fix:")
        print("  poetry install")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
