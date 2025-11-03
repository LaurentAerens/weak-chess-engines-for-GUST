import chess
import random
import sys
import os
import sqlite3
import threading

try:
    from ..base_engine import BaseUCIEngine
except Exception:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) )
    from base_engine import BaseUCIEngine

class RareOpeningBookEngine(BaseUCIEngine):
    def __init__(self, book_path=None):
        super().__init__("RareOpeningBook", "Laurent Aerens")
        self.book = {}
        self.db = None
        self._db_lock = None
        # If an explicit path is given, load it. Otherwise try the package default
        if book_path:
            if os.path.isdir(book_path):
                dbp = os.path.join(book_path, 'opening_book_rare.db')
                jgz = os.path.join(book_path, 'opening_book_rare.json.gz')
                if os.path.exists(dbp):
                    self.load_book(dbp)
                elif os.path.exists(jgz):
                    self.load_book(jgz)
                else:
                    self.load_book(book_path)
            else:
                self.load_book(book_path)
        else:
            book_dir = os.path.join(os.path.dirname(__file__), 'book')
            db_default = os.path.join(book_dir, 'opening_book_rare.db')
            json_default = os.path.join(book_dir, 'opening_book_rare.json.gz')
            if os.path.exists(db_default):
                self.load_book(db_default)
            elif os.path.exists(json_default):
                self.load_book(json_default)
            else:
                pass

    def load_book(self, path):
        try:
            lower = path.lower()
            if lower.endswith('.db'):
                try:
                    uri = f'file:{os.path.abspath(path)}?mode=ro'
                    self.db = sqlite3.connect(uri, uri=True, check_same_thread=False, timeout=30)
                    self._db_lock = threading.RLock()
                    try:
                        self.db.execute('PRAGMA query_only = ON;')
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[RareOpeningBook] Failed to open sqlite DB {path}: {e}", file=sys.stderr)
                    self.db = None
                self.book = {}
                return
            # no other formats supported
            raise ValueError(f"Unsupported book format: {path}")
        except Exception as e:
            print(f"[RareOpeningBook] Failed to load book from {path}: {e}", file=sys.stderr)
            self.book = {}
            if self.db:
                try:
                    self.db.close()
                except Exception:
                    pass
                self.db = None

    def get_best_move(self, think_time: float = 1.0):
        key = ' '.join(self.board.fen().split(' ')[:4])
        move_uci = None
        if self.db:
            try:
                lock = self._db_lock
                if lock is None:
                    lock = threading.RLock()
                    self._db_lock = lock
                with lock:
                    cur = self.db.cursor()
                    cur.execute('SELECT move FROM rare_book WHERE hash = ?', (key,))
                    row = cur.fetchone()
                    if row:
                        move_uci = row[0]
                    cur.close()
            except Exception as e:
                print(f"[RareOpeningBook] SQLite lookup error: {e}", file=sys.stderr)
        if not move_uci and self.book:
            move_uci = self.book.get(str(key)) or self.book.get(key)
        if move_uci:
            try:
                move = chess.Move.from_uci(move_uci)
            except Exception as e:
                print(f"[RareOpeningBook] Failed to parse move from UCI '{move_uci}': {e}", file=sys.stderr)
                move = None
            if move is not None and move in self.board.legal_moves:
                return move
        legal = list(self.board.legal_moves)
        if not legal:
            return None
        return random.choice(legal)

    def close(self):
        if self.db:
            try:
                self.db.close()
            except Exception:
                pass
            self.db = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

if __name__ == '__main__':
    e = RareOpeningBookEngine()
    e.uci_loop()
