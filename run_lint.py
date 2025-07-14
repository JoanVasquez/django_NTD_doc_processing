#!/usr/bin/env python3
"""Code quality checking script for the document processor project."""

import subprocess
import sys


def run_isort() -> int:
    """Run isort to check import sorting."""
    print("Checking import sorting with isort...")
    cmd = ["python", "-m", "isort", "--check-only", "--diff", "api", "documents", "doc_processor"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print("Import sorting is correct!")
        else:
            print("Import sorting issues found. Run: python -m isort api documents doc_processor")
        return result.returncode
    except FileNotFoundError:
        print("isort not found. Install with: pip install -r requirements.dev.txt")
        return 1

def run_flake8() -> int:
    """Run flake8 for code linting."""
    print("Running flake8 linting...")
    cmd = ["python", "-m", "flake8", "api", "documents", "doc_processor"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print("Code linting passed!")
        else:
            print("Linting issues found!")
        return result.returncode
    except FileNotFoundError:
        print("flake8 not found. Install with: pip install -r requirements.dev.txt")
        return 1

def main() -> int:
    """Run all code quality checks."""
    print("Running code quality checks...\n")
    
    isort_result = run_isort()
    print()
    flake8_result = run_flake8()
    
    if isort_result == 0 and flake8_result == 0:
        print("\nAll code quality checks passed!")
        return 0
    else:
        print("\nSome checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())