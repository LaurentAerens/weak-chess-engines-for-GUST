import chess
import random
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine

class SinglePlayerEngine(BaseUCIEngine):
    def __init__(self):
        super().__init__("SinglePlayer", "Laurent Aerens")

    def get_best_move(self, think_time: float = 1.0):
        # Only look ahead 4 ply, always assuming it's our turn
        best_moves = []
        best_score = float('-inf')
        best_opp_value = float('inf')
        board = self.board
        # aggressive pruning parameters
        initial_alpha = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            # quick checkmate short-circuit
            if board.is_checkmate():
                board.pop()
                return move
            score, opp_value = self._single_player_search(board, depth=3, alpha=initial_alpha)
            board.pop()
            # Prefer maximizing own score, then minimizing opponent value
            if (score > best_score) or (score == best_score and opp_value < best_opp_value):
                best_score = score
                best_opp_value = opp_value
                best_moves = [move]
            elif score == best_score and opp_value == best_opp_value:
                best_moves.append(move)
        if not best_moves:
            return None
        return random.choice(best_moves)

    def _single_player_search(self, board, depth, alpha=float('-inf')):
        """Maximizing-only search with alpha-style pruning using a cheap static estimate.

        Args:
            board: chess.Board at current node
            depth: remaining ply (we treat each recursion as our move)
            alpha: current pruning threshold (best score to beat)

        Returns: (best_score, best_opp_value)
        """
        if depth == 0 or board.is_game_over():
            return self._material_score(board), self._opponent_piece_value(board)

        best_score = float('-inf')
        best_opp_value = float('inf')

        # Move ordering: evaluate a cheap static estimate for each move and sort
        moves = list(board.legal_moves)
        def static_estimate_for_move(m):
            # quick heuristic: material after move (for us) plus small bonus for promotions/check
            board.push(m)
            val = self._material_score(board)
            if board.is_check():
                val += 0.5
            # very rough upper bound: assume we can gain a bit for remaining depth
            val += 0.2 * depth
            board.pop()
            return val

        moves.sort(key=static_estimate_for_move, reverse=True)

        # Aggressive width limits per depth (deeper -> fewer moves)
        # depth roughly 3 -> allow more moves; depth 1 -> few moves
        width_by_depth = {3: 8, 2: 6, 1: 4}
        max_width = width_by_depth.get(depth, 6)
        moves = moves[:max_width]

        for move in moves:
            # static upper bound check: if even the static estimate can't beat alpha, prune
            static_est = static_estimate_for_move(move)
            if static_est <= alpha:
                # very aggressive prune
                continue

            board.push(move)
            # recurse with current alpha (we only prune if child can't beat alpha)
            score, opp_value = self._single_player_search(board, depth-1, alpha)
            board.pop()

            if (score > best_score) or (score == best_score and opp_value < best_opp_value):
                best_score = score
                best_opp_value = opp_value
                # update alpha to the new best (tighten pruning for siblings)
                if best_score > alpha:
                    alpha = best_score

            # very aggressive early stop: if we reach a clearly dominant score, return early
            if best_score >= 1000:  # sentinel for forced mate-like values (unlikely here)
                break

        return best_score, best_opp_value

    def _material_score(self, board):
        # Simple material count for the side to move
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3.2, chess.ROOK: 4.8, chess.QUEEN: 9}
        score = 0
        for piece_type in values:
            score += len(board.pieces(piece_type, board.turn)) * values[piece_type]
        return score

    def _opponent_piece_value(self, board):
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3.2, chess.ROOK: 4.8, chess.QUEEN: 9}
        opp_color = not board.turn
        score = 0
        for piece_type in values:
            score += len(board.pieces(piece_type, opp_color)) * values[piece_type]
        return score
