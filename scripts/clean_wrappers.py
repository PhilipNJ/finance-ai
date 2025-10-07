#!/usr/bin/env python3
"""
Remove deprecated root wrapper modules and duplicate scripts.
This enforces `finance_ai/` as the single source of truth and `scripts/` for utilities.
"""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES = [
    "app.py",
    "agents.py",
    "finance_db.py",
    "file_scanner.py",
    "llm_handler.py",
    "parsers.py",
    "utils.py",
    "preflight_check.py",
    "test_installation.py",
    "check_db.py",
    # Optionally remove requirements.txt to avoid drift; it can be exported via Makefile
    "requirements.txt",
]

def main() -> int:
    deleted = []
    skipped = []
    for rel in FILES:
        p = ROOT / rel
        try:
            if p.exists():
                if p.is_file():
                    p.unlink()
                    deleted.append(rel)
                else:
                    skipped.append(rel)
            else:
                skipped.append(rel)
        except Exception as e:
            print(f"⚠️  Failed to remove {rel}: {e}")
            skipped.append(rel)
    print("\nCleanup summary:")
    if deleted:
        print("  ✅ Deleted:")
        for f in deleted:
            print(f"    - {f}")
    if skipped:
        print("  ℹ️  Skipped (not found or not a file):")
        for f in skipped:
            print(f"    - {f}")
    print("\nDone. If you need requirements.txt, regenerate it with: make export-reqs")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
