"""
Alphabetical Engine - Always picks the first move in alphabetical order.
This engine sorts all legal moves by algebraic notation and picks the first one.
"""

import time
from typing import Optional, List
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class AlphabeticalEngine(BaseUCIEngine):
    """Engine that always plays the first move alphabetically."""
    
    def __init__(self):
        super().__init__("Alphabetical Engine", "Laurent Aerens")
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Return the first move alphabetically by algebraic notation."""
        # Simulate some thinking time
        time.sleep(min(think_time, 0.2))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # Convert moves to algebraic notation and sort
        move_notations = []
        for move in legal_moves:
            # Get the algebraic notation for this move
            notation = self.board.san(move)
            move_notations.append((notation, move))
        
        # Sort by algebraic notation (alphabetically)
        move_notations.sort(key=lambda x: x[0])
        
        # Return the first move alphabetically
        return move_notations[0][1]


if __name__ == "__main__":
    run_engine(AlphabeticalEngine)