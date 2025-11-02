import chess
import random
import time
import sys
import os

# allow importing base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine


class MirrorYEngine(BaseUCIEngine):
    """
    Tries to reach a position that is as close as possible to the mirror of
    the opponent's position across the Y (vertical) axis. Picks randomly
    among equally good moves. If no legal move improves mirrorness, plays
    a random legal move.
    """
    def __init__(self):
        super().__init__("Mirror Y Engine", "Laurent Aerens")

    def mirror_board(self, board: chess.Board) -> chess.Board:
        # Create an empty board and place mirrored pieces
        target = chess.Board()
        target.clear()
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece:
                r = chess.square_rank(sq)
                f = chess.square_file(sq)
                # Mirror across the horizontal axis (flip ranks) so moves are copied
                mirror_r = 7 - r
                mirror_sq = chess.square(f, mirror_r)
                # place same piece type but swapped color on mirrored square
                # (we want our pieces to occupy the mirrored squares of the opponent)
                target.set_piece_at(mirror_sq, chess.Piece(piece.piece_type, not piece.color))
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
