"""
Pi Engine - Uses the mathematical constant Pi to select moves.
This engine picks moves based on Pi's digits mapped to the move list index.
"""

import time
from typing import Optional
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class PiEngine(BaseUCIEngine):
    """Engine that uses Pi (3.14159265358979...) to select moves."""
    
    def __init__(self):
        super().__init__("Pi Engine", "Laurent Aerens")
        # Pi constant with high precision
        self.pi = 3.14159265358979323846264338327950288419716939937510
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Return move based on Pi's fractional part mapped to move list."""
        # Simulate some thinking time
        time.sleep(min(think_time, 0.2))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        num_moves = len(legal_moves)
        
        # Use Pi to calculate the index
        # Pi = 3.14159..., so we use the fractional part (0.14159...)
        # Multiply by num_moves and round down to get index
        fractional_part = self.pi - int(self.pi)  # 0.14159...
        index = int(fractional_part * num_moves)
        
        # Ensure index is within bounds
        index = min(index, num_moves - 1)
        
        return legal_moves[index]


if __name__ == "__main__":
    run_engine(PiEngine)