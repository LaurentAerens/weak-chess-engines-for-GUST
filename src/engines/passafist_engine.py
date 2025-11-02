import chess
import random
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine

class PassafistEngine(BaseUCIEngine):
    """
    Plays any move that is NOT checkmate, check, capture, or push (move closer to enemy backline).
    If no such move exists, prefers push, then capture, then check, then checkmate (reverse CCCP order).
    """
    def __init__(self):
        super().__init__("Passafist Engine", "Laurent Aerens")

    def get_best_move(self, think_time: float = 0):
        time.sleep(min(think_time, 0.1))
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        # 1. Non-checkmate, non-check, non-capture, non-push moves
        non_special_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            is_checkmate = b.is_checkmate()
            is_check = b.is_check()
            is_capture = self.board.is_capture(move)
            piece = self.board.piece_at(move.from_square)
            is_push = False
            if piece:
                from_rank = chess.square_rank(move.from_square)
                to_rank = chess.square_rank(move.to_square)
                if self.board.turn == chess.WHITE and to_rank > from_rank:
                    is_push = True
                elif self.board.turn == chess.BLACK and to_rank < from_rank:
                    is_push = True
            if not (is_checkmate or is_check or is_capture or is_push):
                non_special_moves.append(move)
        if non_special_moves:
            return random.choice(non_special_moves)
        # 2. Push moves
        push_moves = []
        for move in legal_moves:
            piece = self.board.piece_at(move.from_square)
            if piece:
                from_rank = chess.square_rank(move.from_square)
                to_rank = chess.square_rank(move.to_square)
                if self.board.turn == chess.WHITE and to_rank > from_rank:
                    push_moves.append(move)
                elif self.board.turn == chess.BLACK and to_rank < from_rank:
                    push_moves.append(move)
        if push_moves:
            return random.choice(push_moves)
        # 3. Capture moves
        capture_moves = [m for m in legal_moves if self.board.is_capture(m)]
        if capture_moves:
            return random.choice(capture_moves)
        # 4. Check moves
        check_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            if b.is_check():
                check_moves.append(move)
        if check_moves:
            return random.choice(check_moves)
        # 5. Checkmate moves
        checkmate_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            if b.is_checkmate():
                checkmate_moves.append(move)
        if checkmate_moves:
            return random.choice(checkmate_moves)
        # Otherwise, pick any legal move
        return random.choice(legal_moves)
