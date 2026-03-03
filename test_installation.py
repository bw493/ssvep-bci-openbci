#!/usr/bin/env python3
"""
Test script to verify SSVEP BCI installation
Checks all modules can be imported correctly
"""

import sys
import os

print("="*60)
print("SSVEP BCI System - Installation Test")
print("="*60 + "\n")

# Test imports
modules_to_test = [
    ('config', 'Configuration'),
    ('preprocessing', 'Preprocessing'),
    ('features', 'Feature Extraction'),
    ('classification', 'Classification'),
    ('control', 'Device Control')
]

all_passed = True

for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"✓ {description:25s} - OK")
    except ImportError as e:
        print(f"✗ {description:25s} - FAILED: {e}")
        all_passed = False

print("\n" + "-"*60)

# Test dependencies
print("\nChecking Python Dependencies:")

dependencies = [
    'mne',
    'numpy',
    'scipy',
    'sklearn',
    'matplotlib',
    'pandas',
    'serial'
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ {dep:15s} - OK")
    except ImportError:
        print(f"✗ {dep:15s} - MISSING")
        all_passed = False

print("\n" + "="*60)

if all_passed:
    print("✓ All tests passed! System is ready to use.")
    print("\nNext steps:")
    print("1. Generate test data:")
    print("   python scripts/generate_test_data.py")
    print("\n2. Run the pipeline:")
    print("   python scripts/run_pipeline.py")
else:
    print("✗ Some tests failed. Please install missing dependencies:")
    print("   pip install -r requirements.txt")

print("="*60 + "\n")

sys.exit(0 if all_passed else 1)
