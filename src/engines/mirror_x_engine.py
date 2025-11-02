import chess
import random
import time
import sys
import os

# allow importing base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine


class MirrorXEngine(BaseUCIEngine):
    """
    Tries to reach a position that is as close as possible to the mirror of
    the opponent's position across the X (vertical) axis. Picks randomly
    among equallX good moves. If no legal move improves mirrorness, plays
    a random legal move.
    """
    def __init__(self):
        super().__init__("Mirror X Engine", "Laurent Aerens")

    def mirror_board(self, board: chess.Board) -> chess.Board:
        # Create an empty board and place mirrored pieces (across files)
        target = chess.Board()
        target.clear()
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece:
                r = chess.square_rank(sq)
                f = chess.square_file(sq)
                # Mirror across the vertical axis (flip files)
                mirror_f = 7 - f
                mirror_sq = chess.square(mirror_f, r)
                # place same piece type and color on mirrored square
                target.set_piece_at(mirror_sq, chess.Piece(piece.piece_type, piece.color))
        # Keep turn consistent
        target.turn = board.turn
        return target

    def board_similarity(self, a: chess.Board, b: chess.Board) -> int:
        # Unweighted similarity: each correct piece placement counts as 1 point
        score = 0
        for sq in chess.SQUARES:
            p_a = a.piece_at(sq)
            p_b = b.piece_at(sq)
            if p_a and p_b and p_a.piece_type == p_b.piece_type and p_a.color == p_b.color:
                score += 1
        return score

    def get_best_move(self, think_time: float):
        # small think
        time.sleep(min(think_time, 0.1))

        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None

        # Mirror the current board (which is the position after opponent moved)
        target = self.mirror_board(self.board)

        best_score = -1
        best_moves = []
        for move in legal_moves:
            b = self.board.copy()
            b.push(move)
            s = self.board_similarity(b, target)
            if s > best_score:
                best_score = s
                best_moves = [move]
            elif s == best_score:
                best_moves.append(move)

        if best_moves:
            return random.choice(best_moves)

        return random.choice(legal_moves)
