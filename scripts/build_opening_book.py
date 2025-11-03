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
import glob
import chess.pgn


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


def main():
    # Default input folder: scripts/pgns/*.pgn
    # Default output: src/engines/book/opening_book.json.gz
    default_pgn_dir = os.path.join(os.path.dirname(__file__), 'pgns')
    default_out = os.path.join(os.path.dirname(__file__), '..', 'src', 'engines', 'book', 'opening_book.json.gz')

    if len(sys.argv) == 1:
        # no args: use defaults
        pgns = sorted(glob.glob(os.path.join(default_pgn_dir, '*.pgn')))
        outpath = default_out
    elif len(sys.argv) == 2:
        # single arg: output path provided, read all PGNs in default dir
        outpath = sys.argv[1]
        pgns = sorted(glob.glob(os.path.join(default_pgn_dir, '*.pgn')))
    else:
        outpath = sys.argv[1]
        pgns = sys.argv[2:]

    print(f"Building book from {len(pgns)} PGN files...")
    book = build_book(pgns)
    print(f"Positions in book: {len(book)}")
    # Ensure output directory exists
    outdir = os.path.dirname(outpath)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    with gzip.open(outpath, 'wt', encoding='utf-8') as gz:
        json.dump(book, gz)
    print(f"Wrote book to {outpath}")

if __name__ == '__main__':
    main()
