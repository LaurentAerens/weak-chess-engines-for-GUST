"""
Blunder Engine - Actively looks for the worst moves to play.
This engine evaluates positions and deliberately chooses bad moves.
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


class BlunderEngine(BaseUCIEngine):
    """Engine that deliberately plays bad moves."""
    
    def __init__(self):
        super().__init__("Blunder Master", "Laurent Aerens")
        
        # Piece values for evaluation
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Simple material evaluation."""
        if board.is_checkmate():
            return -999999 if board.turn else 999999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        score = 0
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
            
        return score
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Return the worst possible move."""
        start_time = time.time()
        
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # If very little time, just return a random move
        if think_time < 0.1:
            return random.choice(legal_moves)
        
        move_scores = []
        current_eval = self.evaluate_position(self.board)
        
        for move in legal_moves:
            if self.stop_thinking or time.time() - start_time > think_time * 0.8:
                break
                
            # Make the move temporarily
            self.board.push(move)
            
            # Evaluate the resulting position
            new_eval = self.evaluate_position(self.board)
            
            # For blundering, we want moves that make our position worse
            if self.board.turn:  # It's Black's turn after our move
                score_change = current_eval - new_eval  # Higher is worse for us
            else:  # It's White's turn after our move
                score_change = new_eval - current_eval  # Higher is worse for us
            
            move_scores.append((move, score_change))
            
            # Undo the move
            self.board.pop()
        
        if not move_scores:
            return random.choice(legal_moves)
        
        # Sort by score change (highest first = worst moves first)
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness - pick from the worst 3 moves
        worst_moves = move_scores[:min(3, len(move_scores))]
        
        # Prefer moves that hang material or allow tactics
        for move, score in worst_moves:
            self.board.push(move)
            
            # Check if this move hangs a piece
            if self._hangs_piece():
                self.board.pop()
                return move
                
            self.board.pop()
        
        # If no hanging pieces, just pick the worst evaluated move
        return worst_moves[0][0]
    
    def _hangs_piece(self) -> bool:
        """Check if the current position has a hanging piece."""
        # Look for undefended pieces that can be captured
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color != self.board.turn:
                # Check if this piece can be captured
                for move in self.board.legal_moves:
                    if move.to_square == square:
                        # Check if the piece is undefended
                        self.board.push(move)
                        attackers = self.board.attackers(piece.color, square)
                        self.board.pop()
                        
                        if not attackers:
                            return True
        return False


if __name__ == "__main__":
    run_engine(BlunderEngine)