#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from engines.paralegal_engine import ParalegalEngine


def main():
    engine = ParalegalEngine()
    engine.uci_loop()


if __name__ == '__main__':
    main()
