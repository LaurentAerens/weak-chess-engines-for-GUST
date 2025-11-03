import chess
import random
import sys
import os

try:
    from ..base_engine import BaseUCIEngine
except Exception:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base_engine import BaseUCIEngine


class ParalegalEngine(BaseUCIEngine):
    """The Paralegal: picks a move that results in the opponent having the largest
    number of legal moves on their next turn. This attempts to maximize the
    opponent's branching factor.
    If several moves tie, one is chosen at random.
    """
    def __init__(self):
        super().__init__("Paralegal", "Laurent Aerens")

    def get_best_move(self, think_time: float = 1.0):
        legal = list(self.board.legal_moves)
        if not legal:
            return None

        best_moves = []
        best_score = -1

        # Evaluate each legal move by counting opponent legal moves after making it
        for move in legal:
            self.board.push(move)
            try:
                # It's opponent's turn now; count their legal moves
                score = len(list(self.board.legal_moves))
            except Exception:
                score = 0
            self.board.pop()

            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return random.choice(best_moves)


if __name__ == '__main__':
    e = ParalegalEngine()
    e.uci_loop()
