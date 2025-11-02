import chess
import random
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine

# Map each piece type and color to its starting square for the opposite color
REVERSE_START_SQUARES = {
    (chess.KING, chess.WHITE): chess.E8,
    (chess.QUEEN, chess.WHITE): chess.D8,
    (chess.ROOK, chess.WHITE): [chess.A8, chess.H8],
    (chess.BISHOP, chess.WHITE): [chess.C8, chess.F8],
    (chess.KNIGHT, chess.WHITE): [chess.B8, chess.G8],
    (chess.PAWN, chess.WHITE): [chess.A7, chess.B7, chess.C7, chess.D7, chess.E7, chess.F7, chess.G7, chess.H7],
    (chess.KING, chess.BLACK): chess.E1,
    (chess.QUEEN, chess.BLACK): chess.D1,
    (chess.ROOK, chess.BLACK): [chess.A1, chess.H1],
    (chess.BISHOP, chess.BLACK): [chess.C1, chess.F1],
    (chess.KNIGHT, chess.BLACK): [chess.B1, chess.G1],
    (chess.PAWN, chess.BLACK): [chess.A2, chess.B2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2],
}

def piece_distance(sq, targets):
    if isinstance(targets, list):
        return min(chess.square_distance(sq, t) for t in targets)
    return chess.square_distance(sq, targets)

class ReverseStartEngine(BaseUCIEngine):
    """
    Tries to minimize the sum of distances between its pieces and the opposite color's starting squares.
    Picks randomly among all best moves. If no move improves, picks randomly.
    """
    def __init__(self):
        super().__init__("Reverse Start Engine", "Laurent Aerens")

    def board_score(self, board: chess.Board, color: bool) -> int:
        score = 0
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == color:
                targets = REVERSE_START_SQUARES.get((piece.piece_type, color))
                if targets:
                    score += piece_distance(sq, targets)
        return score

    def get_best_move(self, think_time: float = 0):
        time.sleep(min(think_time, 0.1))
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        color = self.board.turn
        current_score = self.board_score(self.board, color)
        best_score = current_score
        best_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            s = self.board_score(b, color)
            if s < best_score:
                best_score = s
                best_moves = [move]
            elif s == best_score:
                best_moves.append(move)
        if best_moves and best_score < current_score:
            return random.choice(best_moves)
        return random.choice(legal_moves)
