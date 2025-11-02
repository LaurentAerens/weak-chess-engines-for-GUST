#!/usr/bin/env python3
"""
UCI entry point for Opposite Color Square Engine
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from engines.opposite_color_square_engine import OppositeColorSquareEngine
from base_engine import run_engine

if __name__ == "__main__":
    run_engine(OppositeColorSquareEngine)
