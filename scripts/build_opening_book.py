#!/usr/bin/env python3
"""
Build an opening book from one or more PGN files.
Usage: python scripts/build_opening_book.py outbook.json.gz games1.pgn games2.pgn ...
The output is a gzipped JSON mapping FEN -> best_move_uci (most played move in that FEN).
"""
import sys
import os
import gzip
import json
from collections import Counter, defaultdict
import sqlite3
import glob
import chess.pgn
import time
import argparse
import shutil


## Legacy JSON builder removed: only SQLite DB output is supported


def build_book_sqlite(pgn_paths, outpath, keep_singletons: bool = False):
    """Build an on-disk sqlite3 book by counting moves per Zobrist hash and storing the most-played move.
    Schema:
      counts(hash INTEGER, move TEXT, count INTEGER, PRIMARY KEY(hash, move))
      book(hash INTEGER PRIMARY KEY, move TEXT)
    """
    outdir = os.path.dirname(outpath)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    conn = sqlite3.connect(outpath)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = OFF;")
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("CREATE TABLE IF NOT EXISTS counts(hash TEXT, move TEXT, count INTEGER, PRIMARY KEY(hash, move));")
    conn.commit()

    insert_sql = "INSERT INTO counts(hash, move, count) VALUES (?, ?, 1) ON CONFLICT(hash, move) DO UPDATE SET count = count + 1;"
    ops = 0
    games = 0
    print(f"[build_book_sqlite] Processing {len(pgn_paths)} PGN files...", flush=True)
    for idx, path in enumerate(pgn_paths, start=1):
        print(f"[build_book_sqlite] Reading file {idx}/{len(pgn_paths)}: {path}", flush=True)
        try:
            total_bytes = os.path.getsize(path)
        except Exception:
            total_bytes = 0
        if total_bytes:
            print(f"[build_book_sqlite] File size: {total_bytes} bytes", flush=True)
        file_start = time.time()
        file_games = 0
        file_moves = 0
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                games += 1
                file_games += 1
                board = game.board()
                for move in game.mainline_moves():
                    # Use a normalized FEN (first 4 fields) as the position key. This
                    # is human-readable and avoids integer wrapping issues across
                    # different sqlite/python builds.
                    key = ' '.join(board.fen().split(' ')[:4])
                    u = move.uci()
                    cur.execute(insert_sql, (key, u))
                    ops += 1
                    file_moves += 1
                    if ops % 2000 == 0:
                        conn.commit()
                        pct = None
                        try:
                            if total_bytes:
                                pct = f.tell() * 100.0 / total_bytes
                        except Exception:
                            pct = None
                        if pct is not None:
                            print(f"[build_book_sqlite] Processed {ops} moves, {games} games so far... (file {idx} ~{pct:.1f}% read)", flush=True)
                        else:
                            print(f"[build_book_sqlite] Processed {ops} moves, {games} games so far...", flush=True)
                    board.push(move)
                if file_games % 50 == 0:
                    try:
                        pct = f.tell() * 100.0 / total_bytes if total_bytes else None
                    except Exception:
                        pct = None
                    if pct is not None:
                        print(f"[build_book_sqlite] File {idx}: processed {file_games} games so far, ~{pct:.1f}% of file read", flush=True)
                    else:
                        print(f"[build_book_sqlite] File {idx}: processed {file_games} games so far", flush=True)
        file_time = time.time() - file_start
    conn.commit()
    print(f"[build_book_sqlite] Finished file {idx}/{len(pgn_paths)}: {file_games} games, {file_moves} moves, took {file_time:.2f}s (cumulative moves: {ops})", flush=True)
    conn.commit()
    print(f"[build_book_sqlite] Finished reading PGNs: {games} games, {ops} moves inserted/updated.", flush=True)

    print("[build_book_sqlite] Aggregating most-played move per position into table 'book'...", flush=True)
    cur.execute("DROP TABLE IF EXISTS book;")
    cur.execute("CREATE TABLE book(hash TEXT PRIMARY KEY, move TEXT);")
    if keep_singletons:
        cur.execute(
            "INSERT OR REPLACE INTO book(hash, move)\n"
            "SELECT hash, move FROM (SELECT hash, move, ROW_NUMBER() OVER (PARTITION BY hash ORDER BY count DESC) AS rn FROM counts) WHERE rn = 1;"
        )
    else:
        cur.execute(
            "INSERT OR REPLACE INTO book(hash, move)\n"
            "SELECT c.hash, c.move FROM (SELECT hash, move, ROW_NUMBER() OVER (PARTITION BY hash ORDER BY count DESC) AS rn FROM counts) c\n"
            "JOIN (SELECT hash, SUM(count) AS total_count FROM counts GROUP BY hash HAVING SUM(count) > 1) t ON c.hash = t.hash\n"
            "WHERE c.rn = 1;"
        )
    conn.commit()

    # Fun feature: dump least played move per position if requested
    if getattr(build_book_sqlite, "dump_rare_openings", False):
        print("[build_book_sqlite] Aggregating least-played move per position into table 'rare_book'...", flush=True)
        cur.execute("DROP TABLE IF EXISTS rare_book;")
        cur.execute("CREATE TABLE rare_book(hash TEXT PRIMARY KEY, move TEXT);")
        # Only keep positions seen more than once (prune singletons)
        cur.execute(
            "INSERT OR REPLACE INTO rare_book(hash, move)\n"
            "SELECT c.hash, c.move FROM (SELECT hash, move, ROW_NUMBER() OVER (PARTITION BY hash ORDER BY count ASC) AS rn FROM counts) c\n"
            "JOIN (SELECT hash, SUM(count) AS total_count FROM counts GROUP BY hash HAVING SUM(count) > 1) t ON c.hash = t.hash\n"
            "WHERE c.rn = 1;"
        )
        conn.commit()
        # Dump rare_book to a separate DB file
        rare_db_path = outpath.replace('.db', '_rare.db')
        print(f"[build_book_sqlite] Dumping rare openings to {rare_db_path}", flush=True)
        # Copy schema and rare_book table to new DB
        rare_conn = sqlite3.connect(rare_db_path)
        rare_cur = rare_conn.cursor()
        rare_cur.execute("DROP TABLE IF EXISTS rare_book;")
        rare_cur.execute("CREATE TABLE rare_book(hash TEXT PRIMARY KEY, move TEXT);")
        for row in cur.execute("SELECT hash, move FROM rare_book;"):
            rare_cur.execute("INSERT INTO rare_book(hash, move) VALUES (?, ?);", row)
        rare_conn.commit()
        rare_cur.close()
        rare_conn.close()
        print(f"[build_book_sqlite] Rare opening book created at {rare_db_path}", flush=True)

    print("[build_book_sqlite] Dropping temporary tables to shrink DB...", flush=True)
    cur.execute("DROP TABLE IF EXISTS counts;")
    conn.commit()

    try:
        print("[build_book_sqlite] Running VACUUM to reclaim space...", flush=True)
        cur.execute("VACUUM;")
        conn.commit()
    except Exception as e:
        print(f"[build_book_sqlite] VACUUM failed or not supported: {e}", flush=True)

    print("[build_book_sqlite] Book table created and DB compacted. Closing DB.", flush=True)
    cur.close()
    conn.close()
    return


def main():
    parser = argparse.ArgumentParser(description='Build an opening book from PGN files. Outputs sqlite .db only.')
    parser.add_argument('outpath', nargs='?', help='Output path (.db). If omitted defaults to src/engines/book/opening_book.db')
    parser.add_argument('pgns', nargs='*', help='List of PGN files to read (defaults to scripts/pgns/*.pgn)')
    parser.add_argument('--keep-singletons', action='store_true', help='Do not prune positions that only occur once (default: prune)')
    parser.add_argument('--rare-openings', action='store_true', help='Dump least played move per position to a rare-opening-book DB')
    args = parser.parse_args()

    # Default input folder: scripts/pgns/*.pgn
    default_pgn_dir = os.path.join(os.path.dirname(__file__), 'pgns')
    default_db = os.path.join(os.path.dirname(__file__), '..', 'src', 'engines', 'book', 'opening_book.db')

    if not args.outpath:
        outpath = default_db
    else:
        outpath = args.outpath
        if not outpath.lower().endswith('.db'):
            outpath = outpath + '.db'

    if args.pgns:
        pgns = args.pgns
    else:
        pgns = sorted(glob.glob(os.path.join(default_pgn_dir, '*.pgn')))

    print(f"Building book from {len(pgns)} PGN files...", flush=True)
    # Set feature flag for rare openings
    build_book_sqlite.dump_rare_openings = args.rare_openings
    build_book_sqlite(pgns, outpath, keep_singletons=args.keep_singletons)
    print(f"Wrote sqlite book to {outpath}", flush=True)

if __name__ == '__main__':
    main()
