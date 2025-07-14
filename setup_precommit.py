#!/usr/bin/env python3
"""Setup pre-commit hooks for the project."""

import subprocess
import sys

def setup_precommit() -> int:
    """Install and setup pre-commit hooks."""
    try:
        print("Installing pre-commit hooks...")
        result = subprocess.run(["pre-commit", "install"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Pre-commit hooks installed successfully!")
            print("Hooks will run automatically on git commit.")
            return 0
        else:
            print(f"Failed to install pre-commit hooks: {result.stderr}")
            return 1
            
    except FileNotFoundError:
        print("pre-commit not found. Install with: pip install -r requirements.dev.txt")
        return 1

if __name__ == "__main__":
    sys.exit(setup_precommit())