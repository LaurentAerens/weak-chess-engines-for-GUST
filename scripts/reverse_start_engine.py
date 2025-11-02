"""
Entry point for Reverse Start Engine
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.engines.reverse_start_engine import ReverseStartEngine
from src.base_engine import run_engine

if __name__ == "__main__":
    run_engine(ReverseStartEngine)
