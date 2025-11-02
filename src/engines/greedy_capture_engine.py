"""
Greedy Capture Engine - Always captures if possible, otherwise random.
This engine has a one-track mind focused only on capturing pieces.
"""

import random
import time
from typing import Optional, List
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class GreedyCaptureEngine(BaseUCIEngine):
    """Engine that always captures when possible, ignoring positional considerations."""
    
    def __init__(self):
        super().__init__("Greedy Capture Engine", "Laurent Aerens")
        
        # Piece values for determining capture value
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Always capture the highest value piece if possible."""
        # Simulate some thinking time
        time.sleep(min(think_time, 0.2))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # Find all capture moves
        capture_moves = []
        for move in legal_moves:
            if self.board.is_capture(move):
                captured_piece = self.board.piece_at(move.to_square)
                if captured_piece:
                    value = self.piece_values.get(captured_piece.piece_type, 0)
                    capture_moves.append((move, value))
        
        if capture_moves:
            # Sort by captured piece value (highest first)
            capture_moves.sort(key=lambda x: x[1], reverse=True)
            
            # Among highest value captures, pick randomly
            highest_value = capture_moves[0][1]
            best_captures = [move for move, value in capture_moves if value == highest_value]
            
            return random.choice(best_captures)
        
        # No captures available, make a random move
        # But prefer moves that attack enemy pieces
        attacking_moves = []
        for move in legal_moves:
            self.board.push(move)
            
            # Check if this move attacks any enemy pieces
            attacks_piece = False
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece and piece.color != self.board.turn:
                    if self.board.is_attacked_by(self.board.turn, square):
                        attacks_piece = True
                        break
            
            if attacks_piece:
                attacking_moves.append(move)
            
            self.board.pop()
        
        if attacking_moves:
            return random.choice(attacking_moves)
        
        # No attacks either, just play randomly
        return random.choice(legal_moves)


if __name__ == "__main__":
    run_engine(GreedyCaptureEngine)