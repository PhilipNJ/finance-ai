#!/usr/bin/env python3
"""
Test script to verify agent workflow installation and functionality.
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    errors = []
    
    try:
        import dash
        print("  ✓ dash")
    except ImportError as e:
        errors.append(f"  ✗ dash: {e}")
    
    try:
        import pandas
        print("  ✓ pandas")
    except ImportError as e:
        errors.append(f"  ✗ pandas: {e}")
    
    try:
        import plotly
        print("  ✓ plotly")
    except ImportError as e:
        errors.append(f"  ✗ plotly: {e}")
    
    try:
        import pdfplumber
        print("  ✓ pdfplumber")
    except ImportError as e:
        errors.append(f"  ✗ pdfplumber: {e}")
    
    try:
        from llama_cpp import Llama
        print("  ✓ llama-cpp-python (LLM support available)")
    except ImportError as e:
        print("  ⚠ llama-cpp-python not installed (agent workflow will use fallback)")
    
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    return True


def test_model_file():
    """Test that the model file exists."""
    print("\nTesting model file...")
    model_path = Path("mistral-7b-instruct-v0.1.Q5_0.gguf")
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Model file found: {model_path}")
        print(f"  ✓ Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"  ⚠ Model file not found: {model_path}")
        print("  → Agent workflow will use pattern-based extraction")
        print("  → Download with:")
        print("     wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf")
        return False


def test_directories():
    """Test that required directories exist."""
    print("\nTesting directories...")
    dirs = {
        "data": Path("data"),
        "uploads": Path("data/uploads"),
        "temp": Path("data/temp")
    }
    
    all_exist = True
    for name, path in dirs.items():
        if path.exists() and path.is_dir():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: {path} (missing)")
            all_exist = False
    
    return all_exist


def test_agent_modules():
    """Test that agent modules can be imported."""
    print("\nTesting agent modules...")
    errors = []
    
    try:
        from agents import AgentWorkflow, ExtractionAgent, OrganizerAgent, DatabaseAgent
        print("  ✓ agents.py imported successfully")
        print(f"    - AgentWorkflow")
        print(f"    - ExtractionAgent")
        print(f"    - OrganizerAgent")
        print(f"    - DatabaseAgent")
    except ImportError as e:
        errors.append(f"  ✗ agents.py: {e}")
    
    try:
        from llm_handler import LLMHandler, get_llm_handler, is_llm_available
        print("  ✓ llm_handler.py imported successfully")
        
        llm_available = is_llm_available()
        if llm_available:
            print("    - LLM support: Available")
        else:
            print("    - LLM support: Not available (llama-cpp-python not installed)")
    except ImportError as e:
        errors.append(f"  ✗ llm_handler.py: {e}")
    
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    return True


def test_database():
    """Test database functionality."""
    print("\nTesting database...")
    try:
        from finance_db import init_db, get_conn
        init_db()
        print("  ✓ Database initialized")
        
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"  ✓ Tables found: {', '.join(tables)}")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def test_agent_workflow():
    """Test agent workflow instantiation."""
    print("\nTesting agent workflow instantiation...")
    try:
        from agents import AgentWorkflow
        from pathlib import Path
        
        temp_dir = Path("data/temp")
        workflow = AgentWorkflow(temp_dir)
        print("  ✓ AgentWorkflow instantiated successfully")
        print(f"    - ExtractionAgent: {type(workflow.extraction_agent).__name__}")
        print(f"    - OrganizerAgent: {type(workflow.organizer_agent).__name__}")
        print(f"    - DatabaseAgent: {type(workflow.database_agent).__name__}")
        return True
    except Exception as e:
        print(f"  ✗ Agent workflow error: {e}")
        return False


def test_sample_extraction():
    """Test extraction with sample data."""
    print("\nTesting sample extraction...")
    try:
        from agents import ExtractionAgent
        from pathlib import Path
        
        agent = ExtractionAgent(Path("data/temp"))
        
        # Test CSV extraction
        sample_csv = b"date,amount,description\n2025-10-01,-45.67,Test Transaction\n"
        result = agent._extract_from_csv(sample_csv)
        
        if result.get('type') == 'csv' and 'rows' in result:
            print("  ✓ CSV extraction works")
            print(f"    - Extracted {len(result['rows'])} rows")
        else:
            print("  ⚠ CSV extraction returned unexpected format")
        
        # Test text extraction
        sample_text = b"Test text content"
        result = agent._extract_from_text(sample_text)
        
        if result.get('type') == 'text' and 'text' in result:
            print("  ✓ Text extraction works")
        else:
            print("  ⚠ Text extraction returned unexpected format")
        
        return True
    except Exception as e:
        print(f"  ✗ Extraction test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Finance AI - Agent Workflow Installation Test")
    print("=" * 60)
    print()
    
    results = {
        "Imports": test_imports(),
        "Model File": test_model_file(),
        "Directories": test_directories(),
        "Agent Modules": test_agent_modules(),
        "Database": test_database(),
        "Agent Workflow": test_agent_workflow(),
        "Sample Extraction": test_sample_extraction()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Agent workflow is ready to use.")
        print("\nTo start the app:")
        print("  python app.py")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nTo fix issues:")
        print("  1. Run: ./setup.sh")
        print("  2. Install missing dependencies")
        print("  3. Download model file if needed")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
