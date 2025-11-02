import chess
import random
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine

class CCCPEngine(BaseUCIEngine):
    """
    Prioritizes moves in the following order:
    1) Checkmate
    2) Check
    3) Capture
    4) Push (move closer to enemy backline)
    Picks randomly among equally good moves.
    """
    def __init__(self):
        super().__init__("CCCP Engine", "Laurent Aerens")

    def get_best_move(self, think_time: float = 0):
        time.sleep(min(think_time, 0.1))
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        # 1. Checkmate moves
        knight_checkmate_moves = []
        queen_checkmate_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            if b.is_checkmate():
                if move.promotion == chess.KNIGHT:
                    knight_checkmate_moves.append(move)
                elif move.promotion == chess.QUEEN or move.promotion is None:
                    queen_checkmate_moves.append(move)
        if knight_checkmate_moves:
            return random.choice(knight_checkmate_moves)
        if queen_checkmate_moves:
            return random.choice(queen_checkmate_moves)
        # 2. Check moves
        knight_check_moves = []
        queen_check_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            if b.is_check():
                if move.promotion == chess.KNIGHT:
                    knight_check_moves.append(move)
                elif move.promotion == chess.QUEEN or move.promotion is None:
                    queen_check_moves.append(move)
        if knight_check_moves:
            return random.choice(knight_check_moves)
        if queen_check_moves:
            return random.choice(queen_check_moves)
        # 3. Capture moves
        capture_moves = [m for m in legal_moves if self.board.is_capture(m)]
        if capture_moves:
            return random.choice(capture_moves)
        # 4. Push moves (move closer to enemy backline)
        push_moves = []
        for move in legal_moves:
            piece = self.board.piece_at(move.from_square)
            if piece:
                from_rank = chess.square_rank(move.from_square)
                to_rank = chess.square_rank(move.to_square)
                # Only consider moves that move closer to enemy backline
                if self.board.turn == chess.WHITE and to_rank > from_rank:
                    push_moves.append(move)
                elif self.board.turn == chess.BLACK and to_rank < from_rank:
                    push_moves.append(move)
        if push_moves:
            return random.choice(push_moves)
        # Otherwise, pick any legal move
        return random.choice(legal_moves)
