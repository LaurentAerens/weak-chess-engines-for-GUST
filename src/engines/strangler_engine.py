import chess
from base_engine import BaseUCIEngine

class StranglerEngine(BaseUCIEngine):
    def __init__(self):
        super().__init__("Strangler", "Laurent Aerens")

    def get_best_move(self, think_time: float = 1.0):
        best_move = None
        min_opponent_moves = float('inf')
        board = self.board
        for move in board.legal_moves:
            board.push(move)
            opponent_moves = len(list(board.legal_moves))
            board.pop()
            if opponent_moves < min_opponent_moves:
                min_opponent_moves = opponent_moves
                best_move = move
        return best_move
