"""
Color Square Engine - Tries to move all its pieces onto squares matching its own color (white or black).
"""
import time
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine

class ColorSquareEngine(BaseUCIEngine):
    """Engine that tries to get all its pieces onto squares matching its own color."""
    def __init__(self):
        super().__init__("Color Square Engine", "Laurent Aerens")

    def get_best_move(self, think_time: float):
        time.sleep(min(think_time, 0.2))
        if self.stop_thinking:
            return None
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        # Determine our color
        my_color = self.board.turn
        # White wants pieces on white squares, black on black squares
        def is_white_square(square):
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            # In python-chess, A1 is black, so white squares are (rank + file) % 2 == 1
            return (rank + file) % 2 == 1

        def is_my_color_square(square):
            is_white = is_white_square(square)
            return is_white if my_color == chess.WHITE else not is_white
        # Score moves by how many pieces end up on matching color squares
        best_score = -float('inf')
        best_move = legal_moves[0]
        for move in legal_moves:
            test_board = self.board.copy()
            test_board.push(move)
            score = 0
            for square in chess.SQUARES:
                piece = test_board.piece_at(square)
                if piece and piece.color == my_color:
                    if is_my_color_square(square):
                        score += 1
            # Prefer moves that move a piece onto a matching color square
            if is_my_color_square(move.to_square):
                score += 2
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

if __name__ == "__main__":
    run_engine(ColorSquareEngine)
