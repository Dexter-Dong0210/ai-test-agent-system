#!/usr/bin/env python3
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Check required packages
try:
    import openpyxl
    print("openpyxl is available")
except ImportError:
    print("openpyxl is NOT available")