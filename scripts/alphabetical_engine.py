#!/usr/bin/env python3
"""
Entry point for Alphabetical Engine
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engines.alphabetical_engine import AlphabeticalEngine, run_engine

if __name__ == "__main__":
    run_engine(AlphabeticalEngine)