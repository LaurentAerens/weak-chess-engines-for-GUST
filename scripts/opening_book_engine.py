#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from engines.opening_book_engine import OpeningBookEngine

def main():
    # Allow specifying a book path via env var or default location
    import os
    book = os.environ.get('OPENING_BOOK_PATH')
    if not book:
        book = str(Path(__file__).parent.parent / 'src' / 'engines' / 'book' / 'opening_book.json.gz')
    engine = OpeningBookEngine(book if os.path.exists(book) else None)
    engine.uci_loop()

if __name__ == '__main__':
    main()
