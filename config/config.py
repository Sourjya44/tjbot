#!/usr/bin/env python3

# Copyright 2026-present TJBot Contributors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
