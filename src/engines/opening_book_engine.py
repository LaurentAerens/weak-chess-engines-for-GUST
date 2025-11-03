import chess
import random
import gzip
import json
import sys
import os

# When imported as part of the package, use package-relative import
try:
    from ..base_engine import BaseUCIEngine
except Exception:
    # fallback for direct script execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base_engine import BaseUCIEngine

class OpeningBookEngine(BaseUCIEngine):
    def __init__(self, book_path=None):
        super().__init__("OpeningBook", "Laurent Aerens")
        self.book = {}
        # If an explicit path is given, load it. Otherwise try the package default
        if book_path:
            self.load_book(book_path)
        else:
            default = os.path.join(os.path.dirname(__file__), 'book', 'opening_book.json.gz')
            if os.path.exists(default):
                self.load_book(default)
            else:
                # no default book available; remain quiet
                pass

    def load_book(self, path):
        try:
            with gzip.open(path, 'rt', encoding='utf-8') as gz:
                self.book = json.load(gz)
            # successful load: be quiet in normal operation
        except Exception as e:
            # log load error to stderr
            print(f"[OpeningBook] Failed to load book from {path}: {e}", file=sys.stderr)
            self.book = {}

    def get_best_move(self, think_time: float = 1.0):
        # If no book loaded, play randomly
        if not self.book:
            legal = list(self.board.legal_moves)
            if not legal:
                return None
            return random.choice(legal)

        fen = self.board.fen()
        move_uci = self.book.get(fen)
        # Normal operation: silent lookup
        if move_uci is None:
            pass
        else:
            try:
                move = chess.Move.from_uci(move_uci)
            except Exception as e:
                # parsing failed: log to stderr and skip
                print(f"[OpeningBook] Failed to parse move from UCI '{move_uci}': {e}", file=sys.stderr)
                move = None

            if move is not None:
                if move in self.board.legal_moves:
                    return move
                else:
                    # book move not legal here; skip silently
                    pass
        # fallback random
        legal = list(self.board.legal_moves)
        if not legal:
            return None
        return random.choice(legal)

if __name__ == '__main__':
    # quick smoke: try to load book at src/opening_book.json.gz if present
    import os
    default = os.path.join(os.path.dirname(__file__), 'book', 'opening_book.json.gz')
    e = OpeningBookEngine(book_path=default if os.path.exists(default) else None)
    e.uci_loop()
