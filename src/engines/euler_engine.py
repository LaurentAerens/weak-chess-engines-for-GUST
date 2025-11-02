"""
Euler Engine - Uses Euler's number (e) to select moves.
This engine picks moves based on e's digits mapped to the move list index.
"""

import time
from typing import Optional
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class EulerEngine(BaseUCIEngine):
    """Engine that uses Euler's number e (2.71828182845904...) to select moves."""
    
    def __init__(self):
        super().__init__("Euler Engine", "Laurent Aerens")
        # Euler's number (e) constant with high precision
        self.e = 2.71828182845904523536028747135266249775724709369995
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Return move based on e's fractional part mapped to move list."""
        # Simulate some thinking time
        time.sleep(min(think_time, 0.2))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        num_moves = len(legal_moves)
        
        # Use Euler's number to calculate the index
        # e = 2.71828..., so we use the fractional part (0.71828...)
        # Multiply by num_moves and round down to get index
        fractional_part = self.e - int(self.e)  # 0.71828...
        index = int(fractional_part * num_moves)
        
        # Ensure index is within bounds
        index = min(index, num_moves - 1)
        
        return legal_moves[index]


if __name__ == "__main__":
    run_engine(EulerEngine)