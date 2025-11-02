"""
Suicide King Engine - Tries to get the king as close as possible to the enemy king.
"""
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine


class SuicideKingEngine(BaseUCIEngine):
    """Engine that prioritizes moving its king closer to the opponent's king."""
    
    def __init__(self):
         super().__init__("Suicide King Engine", "Laurent Aerens")
    
    def get_best_move(self, time_limit):
        """
        Select the move that brings our king closest to the opponent's king.
        If no king moves are legal, prioritize moving blocking pieces away or capturing enemy pieces.
        """
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None

        our_king_square = self.board.king(self.board.turn)
        opponent_king_square = self.board.king(not self.board.turn)
        if our_king_square is None or opponent_king_square is None:
            return legal_moves[0]

        def chebyshev_distance(sq1, sq2):
            rank1, file1 = chess.square_rank(sq1), chess.square_file(sq1)
            rank2, file2 = chess.square_rank(sq2), chess.square_file(sq2)
            return max(abs(rank1 - rank2), abs(file1 - file2))

        # Find king moves that get closer
        import random
        king_moves = []
        best_distance = chebyshev_distance(our_king_square, opponent_king_square)
        min_distance = best_distance
        for move in legal_moves:
            if move.from_square == our_king_square:
                test_board = self.board.copy()
                test_board.push(move)
                new_king_square = test_board.king(self.board.turn)
                if new_king_square is not None:
                    dist = chebyshev_distance(new_king_square, opponent_king_square)
                    if dist < min_distance:
                        min_distance = dist
                        king_moves = [move]
                    elif dist == min_distance:
                        king_moves.append(move)
        if king_moves:
            return random.choice(king_moves)

        # If no king move gets closer, prioritize moving blocking pieces or capturing enemy pieces
        # Find squares between our king and enemy king (simple straight line)
        blocking_moves = []
        capture_moves = []
        # Vector from our king to enemy king
        rk1, fk1 = chess.square_rank(our_king_square), chess.square_file(our_king_square)
        rk2, fk2 = chess.square_rank(opponent_king_square), chess.square_file(opponent_king_square)
        dr = rk2 - rk1
        df = fk2 - fk1
        # Only consider direct lines (horizontal, vertical, diagonal)
        line_squares = []
        if dr == 0 or df == 0 or abs(dr) == abs(df):
            step_r = (dr > 0) - (dr < 0)
            step_f = (df > 0) - (df < 0)
            r, f = rk1 + step_r, fk1 + step_f
            while (r, f) != (rk2, fk2):
                sq = chess.square(f, r)
                line_squares.append(sq)
                r += step_r
                f += step_f

        # Find our pieces in between
        for move in legal_moves:
            # If move is a capture, prefer it
            if self.board.is_capture(move):
                capture_moves.append(move)
            # If moving a piece that's in the line between kings, prefer it
            if line_squares and move.from_square in line_squares:
                blocking_moves.append(move)
            # If moving the king pawn (pawn in front of king), prefer it
            if our_king_square is not None:
                king_rank = chess.square_rank(our_king_square)
                king_file = chess.square_file(our_king_square)
                # For white, pawn in front is one rank up; for black, one rank down
                pawn_rank = king_rank + (1 if self.board.turn == chess.WHITE else -1)
                if 0 <= pawn_rank <= 7:
                    pawn_square = chess.square(king_file, pawn_rank)
                    if move.from_square == pawn_square:
                        blocking_moves.append(move)

        # Prefer captures first
        if capture_moves:
            return random.choice(capture_moves)
        # Then prefer blocking piece moves
        if blocking_moves:
            return random.choice(blocking_moves)
        # Otherwise, just play any move
        return random.choice(legal_moves)
