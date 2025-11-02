#!/usr/bin/env python3
"""
Entry point for the Strangler chess engine.
Minimizes the number of moves the opponent can make next turn.
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from engines.strangler_engine import StranglerEngine

def main():
    engine = StranglerEngine()
    engine.uci_loop()

if __name__ == "__main__":
    main()
