"""
Suicide King Engine - Tries to get the king as close as possible to the enemy king.
"""
import chess
import sys
import os

# Add the parent directory to the path to import base_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_engine import BaseUCIEngine


class SuicideKingEngine(BaseUCIEngine):
    """Engine that prioritizes moving its king closer to the opponent's king."""
    
    def __init__(self):
         super().__init__("Suicide King Engine", "Laurent Aerens")
    
    def get_best_move(self, time_limit):
        """
        Select the move that brings our king closest to the opponent's king.
        If no king moves are legal, pick a move that doesn't block the king's path.
        """
        legal_moves = list(self.board.legal_moves)
        
        if not legal_moves:
            return None
        
        # Find both kings
        our_king_square = self.board.king(self.board.turn)
        opponent_king_square = self.board.king(not self.board.turn)
        
        if our_king_square is None or opponent_king_square is None:
            # Fallback if kings not found (shouldn't happen in valid positions)
            return legal_moves[0]
        
        # Calculate Manhattan distance between two squares
        def manhattan_distance(sq1, sq2):
            rank1, file1 = chess.square_rank(sq1), chess.square_file(sq1)
            rank2, file2 = chess.square_rank(sq2), chess.square_file(sq2)
            return abs(rank1 - rank2) + abs(file1 - file2)
        
        # Calculate Chebyshev distance (max of rank/file difference)
        def chebyshev_distance(sq1, sq2):
            rank1, file1 = chess.square_rank(sq1), chess.square_file(sq1)
            rank2, file2 = chess.square_rank(sq2), chess.square_file(sq2)
            return max(abs(rank1 - rank2), abs(file1 - file2))
        
        best_move = None
        best_distance = float('inf')
        
        for move in legal_moves:
            # Make the move on a copy to see the resulting position
            test_board = self.board.copy()
            test_board.push(move)
            
            # Find our king position after the move
            our_king_after = test_board.king(self.board.turn)
            
            if our_king_after is None:
                continue
            
            # Calculate distance after this move
            # Use Chebyshev distance (king move distance) for more aggressive approach
            distance = chebyshev_distance(our_king_after, opponent_king_square)
            
            # Strongly prefer king moves by giving them a huge bonus
            is_king_move = move.from_square == our_king_square
            
            # King moves get massive priority (effectively distance - 100)
            # This ensures king moves that approach are always chosen first
            priority = distance - (100 if is_king_move else 0)
            
            if priority < best_distance:
                best_distance = priority
                best_move = move
        
        return best_move if best_move else legal_moves[0]
