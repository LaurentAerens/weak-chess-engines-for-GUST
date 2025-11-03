#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from engines.lawyer_engine import LawyerEngine


def main():
    engine = LawyerEngine()
    engine.uci_loop()


if __name__ == '__main__':
    main()
