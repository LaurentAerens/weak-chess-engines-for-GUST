#!/usr/bin/env python3
"""
Entry point for the Mover chess engine.
Moves the piece that has been moved least, to the square visited least.
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from engines.mover_engine import MoverEngine

def main():
    engine = MoverEngine()
    engine.uci_loop()

if __name__ == "__main__":
    main()
