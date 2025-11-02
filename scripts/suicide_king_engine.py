#!/usr/bin/env python3
"""
Entry point for the Suicide King chess engine.
Tries to move the king as close as possible to the opponent's king.
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from engines.suicide_king_engine import SuicideKingEngine


def main():
    engine = SuicideKingEngine()
    engine.uci_loop()


if __name__ == "__main__":
    main()
