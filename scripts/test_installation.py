#!/usr/bin/env python3
"""
Test script to verify Finance AI installation and functionality using Poetry package.
"""
import sys
from pathlib import Path


def test_imports():
    print("Testing imports...")
    errors = []
    try:
        import dash  # noqa: F401
        print("  ✓ dash")
    except ImportError as e:
        errors.append(f"  ✗ dash: {e}")
    try:
        import pandas  # noqa: F401
        print("  ✓ pandas")
    except ImportError as e:
        errors.append(f"  ✗ pandas: {e}")
    try:
        import plotly  # noqa: F401
        print("  ✓ plotly")
    except ImportError as e:
        errors.append(f"  ✗ plotly: {e}")
    try:
        import pdfplumber  # noqa: F401
        print("  ✓ pdfplumber")
    except ImportError as e:
        errors.append(f"  ✗ pdfplumber: {e}")
    try:
        import requests  # noqa: F401
        print("  ✓ requests (for optional Ollama)")
    except ImportError as e:
        errors.append(f"  ✗ requests: {e}")
    try:
        from finance_ai.llm_handler import is_llm_available
        print(f"  ✓ Ollama reachable: {is_llm_available()}")
    except Exception:
        print("  ⚠ Ollama check skipped")
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    return True


def test_directories():
    print("\nTesting directories...")
    dirs = {"data": Path("data"), "uploads": Path("data/uploads"), "temp": Path("data/temp")}
    all_exist = True
    for name, path in dirs.items():
        if path.exists() and path.is_dir():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: {path} (missing)")
            all_exist = False
    return all_exist


def test_agent_modules():
    print("\nTesting agent modules...")
    errors = []
    try:
        from finance_ai.agents import AgentWorkflow, ExtractionAgent, OrganizerAgent, DatabaseAgent  # noqa: F401
        print("  ✓ agents.py imported successfully")
        print("    - AgentWorkflow")
        print("    - ExtractionAgent")
        print("    - OrganizerAgent")
        print("    - DatabaseAgent")
    except ImportError as e:
        errors.append(f"  ✗ agents.py: {e}")
    try:
        from finance_ai.llm_handler import get_llm_handler, is_llm_available  # noqa: F401
        print("  ✓ llm_handler.py imported successfully")
    except ImportError as e:
        errors.append(f"  ✗ finance_ai.llm_handler: {e}")
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    return True


def test_database():
    print("\nTesting database...")
    try:
        from finance_ai.finance_db import init_db, get_conn
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
    print("\nTesting agent workflow instantiation...")
    try:
        from finance_ai.agents import AgentWorkflow
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
    print("\nTesting sample extraction...")
    try:
        from finance_ai.agents import ExtractionAgent
        agent = ExtractionAgent(Path("data/temp"))
        sample_csv = b"date,amount,description\n2025-10-01,-45.67,Test Transaction\n"
        result = agent._extract_from_csv(sample_csv)
        if result.get('type') == 'csv' and 'rows' in result:
            print("  ✓ CSV extraction works")
            print(f"    - Extracted {len(result['rows'])} rows")
        else:
            print("  ⚠ CSV extraction returned unexpected format")
        sample_text = b"Test text content"
        result = agent._extract_from_text(sample_text)
        if result.get('type') == 'text' and 'text' in result:
            print("  ✓ Text extraction works")
        else:
            print("  ⚠ Text extraction returned unexpected format")
        return True
    except Exception as e:
        print(f"  ✗ Extraction test error: {e}")
        return False


def main():
    print("=" * 60)
    print("Finance AI - Agent Workflow Installation Test")
    print("=" * 60)
    print()
    results = {
        "Imports": test_imports(),
        "Directories": test_directories(),
        "Agent Modules": test_agent_modules(),
        "Database": test_database(),
        "Agent Workflow": test_agent_workflow(),
        "Sample Extraction": test_sample_extraction(),
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
        print("  poetry run finance-ai")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nTo fix issues:")
        print("  1. Run: poetry install")
        print("  2. Install missing system tools (e.g. tesseract for OCR)")
        print("  3. (Optional) Start Ollama for LLM features: https://ollama.com/")
    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
