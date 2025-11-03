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


def build_book(pgn_paths):
    book = defaultdict(Counter)
    for path in pgn_paths:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                board = game.board()
                for move in game.mainline_moves():
                    fen = board.fen()
                    u = move.uci()
                    book[fen][u] += 1
                    board.push(move)
    # convert to most played
    out = {fen: counter.most_common(1)[0][0] for fen, counter in book.items()}
    return out


def build_book_sqlite(pgn_paths, outpath):
    """Build an on-disk sqlite3 book by counting moves per FEN and storing the most-played move.
    This avoids keeping the whole mapping in memory.
    Schema:
      counts(fen TEXT, move TEXT, count INTEGER, PRIMARY KEY(fen, move))
      book(fen TEXT PRIMARY KEY, move TEXT)
    """
    # ensure output directory exists
    outdir = os.path.dirname(outpath)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    # use sqlite3 with WAL disabled and synchronous=OFF for speed; we're the only writer here
    conn = sqlite3.connect(outpath)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = OFF;")
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("CREATE TABLE IF NOT EXISTS counts(fen TEXT, move TEXT, count INTEGER, PRIMARY KEY(fen, move));")
    conn.commit()

    insert_sql = "INSERT INTO counts(fen, move, count) VALUES (?, ?, 1) ON CONFLICT(fen, move) DO UPDATE SET count = count + 1;"
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
                    fen = board.fen()
                    u = move.uci()
                    cur.execute(insert_sql, (fen, u))
                    ops += 1
                    file_moves += 1
                    # periodic commit to keep WAL size reasonable and show progress
                    if ops % 2000 == 0:
                        conn.commit()
                        # compute approximate percent read for this file
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
                # print per-file progress every 50 games
                if file_games % 50 == 0:
                    try:
                        pct = f.tell() * 100.0 / total_bytes if total_bytes else None
                    except Exception:
                        pct = None
                    if pct is not None:
                        print(f"[build_book_sqlite] File {idx}: processed {file_games} games so far, ~{pct:.1f}% of file read", flush=True)
                    else:
                        print(f"[build_book_sqlite] File {idx}: processed {file_games} games so far", flush=True)
        # end of file
        file_time = time.time() - file_start
    conn.commit()
    print(f"[build_book_sqlite] Finished file {idx}/{len(pgn_paths)}: {file_games} games, {file_moves} moves, took {file_time:.2f}s (cumulative moves: {ops})", flush=True)
    conn.commit()
    print(f"[build_book_sqlite] Finished reading PGNs: {games} games, {ops} moves inserted/updated.", flush=True)

    # create final compact book table with most-played move per fen
    print("[build_book_sqlite] Aggregating most-played move per position into table 'book'...", flush=True)
    # ensure book table exists (will replace if present)
    cur.execute("CREATE TABLE IF NOT EXISTS book(fen TEXT PRIMARY KEY, move TEXT);")
    # Insert top move per fen using a window function to choose highest count.
    # This writes one row per FEN (the most-played move). If the counts table is large
    # this will still be performed on-disk without loading everything into RAM.
    cur.execute(
        "INSERT OR REPLACE INTO book(fen, move) SELECT fen, move FROM (SELECT fen, move, ROW_NUMBER() OVER (PARTITION BY fen ORDER BY count DESC) AS rn FROM counts) WHERE rn = 1;"
    )
    conn.commit()

    # Drop the temporary counts table to free space and ensure final DB only contains 'book'
    print("[build_book_sqlite] Dropping temporary tables to shrink DB...", flush=True)
    cur.execute("DROP TABLE IF EXISTS counts;")
    conn.commit()

    # Run VACUUM to reclaim space on disk so DB file doesn't keep freed pages
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
    parser = argparse.ArgumentParser(description='Build an opening book from PGN files. Outputs gzipped JSON or sqlite .db')
    parser.add_argument('outpath', nargs='?', help='Output path (.json.gz or .db). If omitted defaults to src/engines/book/opening_book.json.gz')
    parser.add_argument('pgns', nargs='*', help='List of PGN files to read (defaults to scripts/pgns/*.pgn)')
    parser.add_argument('--db', action='store_true', help='Force sqlite .db output (overrides outpath extension)')
    args = parser.parse_args()

    # Default input folder: scripts/pgns/*.pgn
    default_pgn_dir = os.path.join(os.path.dirname(__file__), 'pgns')
    default_out = os.path.join(os.path.dirname(__file__), '..', 'src', 'engines', 'book', 'opening_book.json.gz')

    if not args.outpath:
        outpath = None
    else:
        outpath = args.outpath

    if args.pgns:
        pgns = args.pgns
    else:
        pgns = sorted(glob.glob(os.path.join(default_pgn_dir, '*.pgn')))

    print(f"Building book from {len(pgns)} PGN files...", flush=True)

    # Default (no outpath): build both outputs
    if outpath is None:
        # sqlite DB will be placed in the same folder as the PGNs (use first PGN dir or default)
        if pgns:
            pgn_dir = os.path.dirname(os.path.abspath(pgns[0]))
        else:
            pgn_dir = default_pgn_dir
        default_db = os.path.join(pgn_dir, 'opening_book.db')
        print(f"No outpath provided — building both JSON.gz and sqlite DB\n  json: {default_out}\n  db:   {default_db}", flush=True)
        build_book_sqlite(pgns, default_db)
        print(f"Wrote sqlite book to {default_db}", flush=True)
        # also copy sqlite DB into the engine book folder so engines can load it by default
        engine_db = os.path.join(os.path.dirname(default_out), 'opening_book.db')
        try:
            if os.path.abspath(default_db) != os.path.abspath(engine_db):
                shutil.copy2(default_db, engine_db)
                print(f"Copied sqlite book to engine folder: {engine_db}", flush=True)
            else:
                print(f"Sqlite book already in engine folder: {engine_db}", flush=True)
        except Exception as e:
            print(f"Warning: failed to copy sqlite book to engine folder: {e}", flush=True)
        book = build_book(pgns)
        print(f"Positions in book: {len(book)}", flush=True)
        # Ensure output directory exists
        outdir = os.path.dirname(default_out)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        with gzip.open(default_out, 'wt', encoding='utf-8') as gz:
            json.dump(book, gz)
        print(f"Wrote book to {default_out}", flush=True)
        return

    # If --db provided or output path endswith .db use SQLite on-disk builder to avoid RAM usage
    if args.db or outpath.lower().endswith('.db'):
        # if user requested --db but provided a non-.db outpath, set to default .db alongside provided name
        if args.db and not outpath.lower().endswith('.db'):
            outpath = outpath + '.db'
        build_book_sqlite(pgns, outpath)
        print(f"Wrote sqlite book to {outpath}", flush=True)
        return

    # otherwise write json.gz to the provided outpath
    book = build_book(pgns)
    print(f"Positions in book: {len(book)}", flush=True)
    # Ensure output directory exists
    outdir = os.path.dirname(outpath)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    with gzip.open(outpath, 'wt', encoding='utf-8') as gz:
        json.dump(book, gz)
    print(f"Wrote book to {outpath}", flush=True)

if __name__ == '__main__':
    main()
