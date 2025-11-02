"""
Shuffle Engine - Prefers to move pieces back and forth without purpose.
This engine creates a shuffling pattern that wastes time and position.
"""

import random
import time
from typing import Optional, Dict
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class ShuffleEngine(BaseUCIEngine):
    """Engine that prefers to shuffle pieces back and forth."""
    
    def __init__(self):
        super().__init__("Shuffle Engine", "Laurent Aerens")
        self.move_history = []  # Track recent moves
        self.piece_positions = {}  # Track where pieces have been
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Prefer moves that shuffle pieces or repeat positions."""
        # Simulate thinking time
        time.sleep(min(think_time, 0.3))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # Update move history
        if len(self.board.move_stack) > 0:
            last_move = self.board.move_stack[-1]
            self.move_history.append(last_move)
            # Keep only recent moves
            if len(self.move_history) > 10:
                self.move_history.pop(0)
        
        # Look for shuffle opportunities
        shuffle_moves = []
        
        for move in legal_moves:
            # Check if this move undoes a recent move (shuffling back)
            if self._is_shuffle_move(move):
                shuffle_moves.append(move)
        
        # If we have shuffle moves, prefer them
        if shuffle_moves:
            return random.choice(shuffle_moves)
        
        # Otherwise, prefer moves that go to squares we've been to before
        familiar_moves = []
        for move in legal_moves:
            piece = self.board.piece_at(move.from_square)
            if piece:
                piece_key = f"{piece.piece_type}_{piece.color}"
                if piece_key in self.piece_positions:
                    if move.to_square in self.piece_positions[piece_key]:
                        familiar_moves.append(move)
        
        if familiar_moves:
            return random.choice(familiar_moves)
        
        # Record where pieces are going for future shuffling
        move = random.choice(legal_moves)
        piece = self.board.piece_at(move.from_square)
        if piece:
            piece_key = f"{piece.piece_type}_{piece.color}"
            if piece_key not in self.piece_positions:
                self.piece_positions[piece_key] = set()
            self.piece_positions[piece_key].add(move.from_square)
            self.piece_positions[piece_key].add(move.to_square)
            
            # Keep set size manageable
            if len(self.piece_positions[piece_key]) > 5:
                self.piece_positions[piece_key] = set(list(self.piece_positions[piece_key])[-5:])
        
        return move
    
    def _is_shuffle_move(self, move: chess.Move) -> bool:
        """Check if this move shuffles a piece back to a recent position."""
        if len(self.move_history) < 2:
            return False
        
        # Check if this move undoes a recent move
        for recent_move in self.move_history[-4:]:  # Check last 4 moves
            if (move.from_square == recent_move.to_square and 
                move.to_square == recent_move.from_square):
                return True
                
            # Also check if we're moving back to a square we recently left
            if move.to_square == recent_move.from_square:
                piece_now = self.board.piece_at(move.from_square)
                if piece_now:
                    # Make the recent move temporarily to check the piece type
                    try:
                        self.board.push(recent_move)
                        piece_then = self.board.piece_at(recent_move.to_square)
                        self.board.pop()
                        
                        if piece_then and piece_now.piece_type == piece_then.piece_type:
                            return True
                    except:
                        pass
        
        return False


if __name__ == "__main__":
    run_engine(ShuffleEngine)