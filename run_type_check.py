#!/usr/bin/env python3
"""Type checking script for the document processor project."""

import subprocess
import sys
from pathlib import Path


def check_dependencies() -> bool:
    """Check if required type checking dependencies are installed."""
    try:
        import mypy  # type: ignore
        return True
    except ImportError:
        print("❌ mypy not found. Install with: pip install -r requirements.dev.txt")
        return False

def run_mypy() -> int:
    """Run mypy type checking on the project."""
    if not check_dependencies():
        return 1
        
    print("🔍 Running strict type checking with mypy...")
    print("⚙️ Configuration: mypy.ini (strict mode enabled)")
    
    # Directories to check
    dirs_to_check = ["api", "documents", "doc_processor"]
    
    # Verify directories exist
    missing_dirs = [d for d in dirs_to_check if not Path(d).exists()]
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return 1
    
    cmd = ["python", "-m", "mypy"] + dirs_to_check
    
    try:
        print(f"📝 Checking directories: {', '.join(dirs_to_check)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print("\n📊 Type checking results:")
            print(result.stdout)
        if result.stderr:
            print("\n⚠️ Warnings/Errors:")
            print(result.stderr, file=sys.stderr)
            
        if result.returncode == 0:
            print("✅ All type checks passed! Your code is strictly typed.")
        else:
            print("❌ Type checking failed. Please fix the issues above.")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running mypy: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_mypy())