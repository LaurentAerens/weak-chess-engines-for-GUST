#!/usr/bin/env python3
"""
Entry point for the Single Player chess engine.
Looks 4 moves ahead, only considers its own moves.
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from engines.single_player_engine import SinglePlayerEngine

def main():
    engine = SinglePlayerEngine()
    engine.uci_loop()

if __name__ == "__main__":
    main()
