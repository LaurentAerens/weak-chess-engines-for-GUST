import chess
import random
import gzip
import json
import sys
import os
import sqlite3
import threading

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
        self.db = None
        self._db_lock = None
        # If an explicit path is given, load it. Otherwise try the package default
        if book_path:
            # if a directory is provided, look inside it for preferred files
            if os.path.isdir(book_path):
                dbp = os.path.join(book_path, 'opening_book.db')
                jgz = os.path.join(book_path, 'opening_book.json.gz')
                if os.path.exists(dbp):
                    self.load_book(dbp)
                elif os.path.exists(jgz):
                    self.load_book(jgz)
                else:
                    # treat provided path as a file path (will be handled by load_book)
                    self.load_book(book_path)
            else:
                # file path provided
                self.load_book(book_path)
        else:
            # default: prefer sqlite DB in package book folder, fallback to json.gz
            book_dir = os.path.join(os.path.dirname(__file__), 'book')
            db_default = os.path.join(book_dir, 'opening_book.db')
            json_default = os.path.join(book_dir, 'opening_book.json.gz')
            if os.path.exists(db_default):
                self.load_book(db_default)
            elif os.path.exists(json_default):
                self.load_book(json_default)
            else:
                # no default book available; remain quiet
                pass

    def load_book(self, path):
        # support three modes:
        #  - gzipped JSON (.json.gz) -> load into RAM (legacy)
        #  - plain JSON (.json) -> load into RAM
        #  - sqlite DB (.db) -> open readonly DB and query per-lookup
        try:
            lower = path.lower()
            if lower.endswith('.db'):
                # open sqlite in read-only mode
                try:
                    # sqlite URI for read-only
                    uri = f'file:{os.path.abspath(path)}?mode=ro'
                    # open read-only with a reasonable timeout; allow cross-thread usage
                    self.db = sqlite3.connect(uri, uri=True, check_same_thread=False, timeout=30)
                    # create a per-connection lock so multiple threads using this instance
                    # serialize access to the sqlite connection/cursors
                    self._db_lock = threading.RLock()
                    # make this connection query-only if supported
                    try:
                        self.db.execute('PRAGMA query_only = ON;')
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[OpeningBook] Failed to open sqlite DB {path}: {e}", file=sys.stderr)
                    self.db = None
                self.book = {}
                return

            if lower.endswith('.json.gz') or lower.endswith('.gz'):
                with gzip.open(path, 'rt', encoding='utf-8') as gz:
                    self.book = json.load(gz)
                return

            # plain json fallback
            with open(path, 'r', encoding='utf-8') as f:
                self.book = json.load(f)
        except Exception as e:
            print(f"[OpeningBook] Failed to load book from {path}: {e}", file=sys.stderr)
            self.book = {}
            if self.db:
                try:
                    self.db.close()
                except Exception:
                    pass
                self.db = None

    def get_best_move(self, think_time: float = 1.0):
        # prefer DB lookup if available to avoid loading whole book
        fen = self.board.fen()
        move_uci = None
        if self.db:
            try:
                # guard access with the per-instance lock to support multithreaded lookups
                lock = self._db_lock
                if lock is None:
                    # defensive: create a lock if missing
                    lock = threading.RLock()
                    self._db_lock = lock
                with lock:
                    cur = self.db.cursor()
                    cur.execute('SELECT move FROM book WHERE fen = ?', (fen,))
                    row = cur.fetchone()
                    if row:
                        move_uci = row[0]
                    cur.close()
            except Exception as e:
                # non-fatal: fall back to in-memory or random
                print(f"[OpeningBook] SQLite lookup error: {e}", file=sys.stderr)

        if not move_uci and self.book:
            move_uci = self.book.get(fen)

        if move_uci:
            try:
                move = chess.Move.from_uci(move_uci)
            except Exception as e:
                print(f"[OpeningBook] Failed to parse move from UCI '{move_uci}': {e}", file=sys.stderr)
                move = None

            if move is not None and move in self.board.legal_moves:
                return move

        # fallback random
        legal = list(self.board.legal_moves)
        if not legal:
            return None
        return random.choice(legal)

    def close(self):
        """Close any open DB connection. Safe to call multiple times."""
        if self.db:
            try:
                self.db.close()
            except Exception:
                pass
            self.db = None

    def __del__(self):
        # best-effort close for temporary objects/tests
        try:
            self.close()
        except Exception:
            pass

if __name__ == '__main__':
    # quick smoke: try to load book at src/opening_book.json.gz if present
    # relying on default discovery (DB preferred, then JSON.gz)
    e = OpeningBookEngine()
    e.uci_loop()
