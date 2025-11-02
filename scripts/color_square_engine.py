#!/usr/bin/env python3
"""
Entry point for the Color Square Engine
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from engines.color_square_engine import ColorSquareEngine, run_engine
if __name__ == "__main__":
    run_engine(ColorSquareEngine)
