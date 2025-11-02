"""
Opposite Color Square Engine - Tries to move all its pieces onto squares of the opposite color (white pieces to black squares, black pieces to white squares).
"""
import time
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine

class OppositeColorSquareEngine(BaseUCIEngine):
    """Engine that tries to get all its pieces onto squares of the opposite color."""
    def __init__(self):
        super().__init__("Opposite Color Square Engine", "Laurent Aerens")

    def get_best_move(self, think_time: float):
        import random
        time.sleep(min(think_time, 0.2))
        if self.stop_thinking:
            return None
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        # Determine our color
        my_color = self.board.turn
        # White wants pieces on black squares, black on white squares
        def is_white_square(square):
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            # In python-chess, A1 is black, so white squares are (rank + file) % 2 == 1
            return (rank + file) % 2 == 1

        def is_opposite_color_square(square):
            is_white = is_white_square(square)
            return not is_white if my_color == chess.WHITE else is_white
        # Score moves by how many pieces end up on opposite color squares
        best_score = -float('inf')
        best_moves = []
        for move in legal_moves:
            test_board = self.board.copy()
            test_board.push(move)
            score = 0
            for square in chess.SQUARES:
                piece = test_board.piece_at(square)
                if piece and piece.color == my_color:
                    if is_opposite_color_square(square):
                        score += 1
            # Prefer moves that move a piece onto an opposite color square
            if is_opposite_color_square(move.to_square):
                score += 2
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        # Always return a move, even if none place a piece on the opposite color square
        if best_moves:
            return random.choice(best_moves)
        else:
            return random.choice(legal_moves)

if __name__ == "__main__":
    run_engine(OppositeColorSquareEngine)
