#!/usr/bin/env python3
"""
TJBot Configuration Tool - Main Executable

Interactive configuration management for TJBot hardware and cloud services.
"""

import sys
import os

# Add the tjconfig package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.cli import main

if __name__ == '__main__':
    sys.exit(main())
