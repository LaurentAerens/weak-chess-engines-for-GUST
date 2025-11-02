"""
Random Engine - Plays completely random legal moves.
This is the weakest possible engine.
"""

import random
import time
from typing import Optional
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine, run_engine


class RandomEngine(BaseUCIEngine):
    """Engine that plays completely random legal moves."""
    
    def __init__(self):
        super().__init__("Random Weak Engine", "Laurent Aerens")
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Return a random legal move."""
        # Simulate some thinking time
        time.sleep(min(think_time, 0.1))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
            
        return random.choice(legal_moves)


if __name__ == "__main__":
    run_engine(RandomEngine)