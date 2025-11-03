import chess
import random
import sys
import os

try:
    from ..base_engine import BaseUCIEngine
except Exception:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base_engine import BaseUCIEngine


class CriminalEngine(BaseUCIEngine):
    """The Criminal: picks a move that results in the fewest legal moves
    (for itself) in the resulting position. This attempts to reduce flexibility
    and can lead to cramped play.
    If several moves tie, one is chosen at random.
    """
    def __init__(self):
        super().__init__("Criminal", "Laurent Aerens")

    def get_best_move(self, think_time: float = 1.0):
        legal = list(self.board.legal_moves)
        if not legal:
            return None

        best_moves = []
        best_score = None

        # Evaluate each legal move by counting legal moves after making it
        for move in legal:
            self.board.push(move)
            try:
                score = len(list(self.board.legal_moves))
            except Exception:
                score = 0
            self.board.pop()

            if best_score is None or score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        # Return a random choice among best scoring moves
        return random.choice(best_moves)


if __name__ == '__main__':
    e = CriminalEngine()
    e.uci_loop()
