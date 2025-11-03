#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from engines.rare_opening_book_engine import RareOpeningBookEngine

def main():
    import os
    book = os.environ.get('RARE_OPENING_BOOK_PATH')
    if not book:
        book = str(Path(__file__).parent.parent / 'src' / 'engines' / 'book' / 'opening_book_rare.db')
    engine = RareOpeningBookEngine(book if os.path.exists(book) else None)
    engine.uci_loop()

if __name__ == '__main__':
    main()
