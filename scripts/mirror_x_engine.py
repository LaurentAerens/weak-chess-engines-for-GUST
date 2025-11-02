#!/usr/bin/env python3
"""
Entry point for Mirror X Engine
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engines.mirror_x_engine import MirrorXEngine, BaseUCIEngine
from base_engine import run_engine

if __name__ == "__main__":
    run_engine(MirrorXEngine)
