#!/usr/bin/env python
"""Fast test runner - runs only lightweight tests"""

import os
import subprocess
import sys


def run_fast_tests():
    """Run only lightweight, fast tests"""
    
    # Set environment variables for faster execution
    os.environ['DJANGO_SETTINGS_MODULE'] = 'doc_processor.settings'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # Skip .pyc files
    
    # Run only lightweight tests
    cmd = [
        'python', '-m', 'pytest',
        'tests/',                       # Test directory
        '-k', 'lightweight',            # Only lightweight tests
        '-v',                           # Verbose
        '--tb=short',                   # Short traceback
        '--disable-warnings',           # Disable warnings
        '--no-cov',                     # Skip coverage for speed
        '-x',                           # Stop on first failure
        '--durations=10'                # Show slowest 10 tests
    ]
    
    print("Running fast tests (lightweight only)...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("All fast tests passed!")
    else:
        print("Some tests failed")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_fast_tests())