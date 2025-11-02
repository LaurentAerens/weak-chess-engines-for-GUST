import chess
from base_engine import BaseUCIEngine

class SinglePlayerEngine(BaseUCIEngine):
    def __init__(self):
        super().__init__("SinglePlayer", "Laurent Aerens")

    def get_best_move(self, think_time: float = 1.0):
        # Only look ahead 4 ply, always assuming it's our turn
        best_move = None
        best_score = float('-inf')
        board = self.board
        for move in board.legal_moves:
            board.push(move)
            score, opp_value = self._single_player_search(board, depth=3)
            board.pop()
            # Checkmate detection
            if board.is_checkmate():
                return move
            # Prefer maximizing own score, then minimizing opponent value
            if (score > best_score) or (score == best_score and opp_value < best_opp_value):
                best_score = score
                best_opp_value = opp_value
                best_move = move
        return best_move

    def _single_player_search(self, board, depth):
        if depth == 0 or board.is_game_over():
            return self._material_score(board), self._opponent_piece_value(board)
        best_score = float('-inf')
        best_opp_value = float('inf')
        for move in board.legal_moves:
            board.push(move)
            score, opp_value = self._single_player_search(board, depth-1)
            board.pop()
            if (score > best_score) or (score == best_score and opp_value < best_opp_value):
                best_score = score
                best_opp_value = opp_value
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
