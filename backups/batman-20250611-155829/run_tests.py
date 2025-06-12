#!/usr/bin/env python3
"""
Test runner for Batman Incorporated.
Adds src to path and runs all tests.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# Run pytest
import pytest

if __name__ == '__main__':
    # Run all tests or specific ones passed as arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else ['tests/', '-v']
    
    sys.exit(pytest.main(args))