import sys
import chess

# Minimal UCI wrapper similar to other scripts
from src.engines.mirror_x_engine import MirrorXEngine

if __name__ == '__main__':
    engine = MirrorXEngine()
    board = chess.Board()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if line == 'uci':
            print('id name MirrorXEngine')
            print('id author Laurent Aerens')
            print('uciok')
        elif line == 'isready':
            print('readyok')
        elif line.startswith('position'):
            parts = line.split()
            if 'startpos' in parts:
                board = chess.Board()
                if 'moves' in parts:
                    mindex = parts.index('moves')
                    for mv in parts[mindex+1:]:
                        board.push_uci(mv)
            else:
                # fen ...
                fen = ' '.join(parts[1:7])
                board = chess.Board(fen)
                if 'moves' in parts:
                    mindex = parts.index('moves')
                    for mv in parts[mindex+1:]:
                        board.push_uci(mv)
        elif line.startswith('go'):
            engine.board = board.copy()
            mv = engine.get_best_move(0.1)
            if mv:
                print('bestmove', mv.uci())
            else:
                print('bestmove 0000')
        elif line == 'quit':
            break
