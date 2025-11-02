"""
Runaway Engine - Tries to maximize the distance between its king and the nearest enemy piece.
"""
import time
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine

class RunawayEngine(BaseUCIEngine):
    """Engine that tries to keep its king as far as possible from enemy pieces."""
    def __init__(self):
        super().__init__("Runaway Engine", "Laurent Aerens")

    def get_best_move(self, think_time: float):
        import random
        time.sleep(min(think_time, 0.2))
        if self.stop_thinking:
            return None
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        my_color = self.board.turn
        # Find king square
        king_square = None
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.piece_type == chess.KING and piece.color == my_color:
                king_square = square
                break
        if king_square is None:
            king_square = 4 if my_color == chess.WHITE else 60  # E1 or E8
        # Find all enemy piece squares
        enemy_squares = [sq for sq in chess.SQUARES if self.board.piece_at(sq) and self.board.piece_at(sq).color != my_color]
        def min_distance(board):
            # After move, find king and all enemy pieces
            king_sq = None
            for sq in chess.SQUARES:
                piece = board.piece_at(sq)
                if piece and piece.piece_type == chess.KING and piece.color == my_color:
                    king_sq = sq
                    break
            if king_sq is None:
                return 0
            enemy_sq = [sq for sq in chess.SQUARES if board.piece_at(sq) and board.piece_at(sq).color != my_color]
            if not enemy_sq:
                return 64  # Max possible distance
            return min(chess.square_distance(king_sq, sq) for sq in enemy_sq)
        best_score = -float('inf')
        best_moves = []
        for move in legal_moves:
            test_board = self.board.copy()
            test_board.push(move)
            score = min_distance(test_board)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        return random.choice(best_moves) if best_moves else random.choice(legal_moves)

if __name__ == "__main__":
    run_engine(RunawayEngine)
