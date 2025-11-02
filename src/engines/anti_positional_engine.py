"""
Anti-Positional Engine - Deliberately plays moves that worsen position.
This engine avoids good positional principles and prefers bad development.
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


class AntiPositionalEngine(BaseUCIEngine):
    """Engine that deliberately violates chess principles."""
    
    def __init__(self):
        super().__init__("Anti-Positional Engine", "Laurent Aerens")
    
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """Choose moves that violate good chess principles."""
        # Simulate thinking time
        time.sleep(min(think_time, 0.4))
        
        if self.stop_thinking:
            return None
            
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        # Categorize moves by how anti-positional they are
        anti_positional_moves = []
        neutral_moves = []
        
        for move in legal_moves:
            score = self._calculate_anti_positional_score(move)
            if score > 0:
                anti_positional_moves.append((move, score))
            else:
                neutral_moves.append(move)
        
        # Prefer anti-positional moves
        if anti_positional_moves:
            # Sort by anti-positional score (higher is worse)
            anti_positional_moves.sort(key=lambda x: x[1], reverse=True)
            
            # Pick from the most anti-positional moves
            worst_score = anti_positional_moves[0][1]
            worst_moves = [move for move, score in anti_positional_moves if score == worst_score]
            
            return random.choice(worst_moves)
        
        # If no specifically anti-positional moves, pick randomly
        return random.choice(neutral_moves)
    
    def _calculate_anti_positional_score(self, move: chess.Move) -> int:
        """Calculate how anti-positional a move is (higher = worse)."""
        score = 0
        piece = self.board.piece_at(move.from_square)
        
        if not piece:
            return 0
        
        # Moving the same piece multiple times in opening
        if len(self.board.move_stack) < 20:  # Still in opening
            moves_with_this_piece = 0
            for past_move in self.board.move_stack:
                past_piece = self.board.piece_at(past_move.to_square)
                if past_piece and past_piece.piece_type == piece.piece_type:
                    moves_with_this_piece += 1
            
            if moves_with_this_piece > 0:
                score += moves_with_this_piece * 2
        
        # Moving pieces to the edge of the board
        file = chess.square_file(move.to_square)
        rank = chess.square_rank(move.to_square)
        
        # Prefer edge squares (anti-central principle)
        if file in [0, 7] or rank in [0, 7]:
            score += 2
        
        # Moving knights to the rim
        if piece.piece_type == chess.KNIGHT:
            if file in [0, 7] or rank in [0, 7]:
                score += 3
        
        # Blocking your own pawns
        if piece.piece_type != chess.PAWN:
            if piece.color == chess.WHITE:
                blocking_square = move.to_square - 8
            else:
                blocking_square = move.to_square + 8
            
            if 0 <= blocking_square < 64:
                blocking_piece = self.board.piece_at(blocking_square)
                if (blocking_piece and 
                    blocking_piece.piece_type == chess.PAWN and 
                    blocking_piece.color == piece.color):
                    score += 3
        
        # Moving developed pieces back to starting squares
        starting_squares = {
            chess.WHITE: {
                chess.KNIGHT: [chess.B1, chess.G1],
                chess.BISHOP: [chess.C1, chess.F1],
                chess.ROOK: [chess.A1, chess.H1],
                chess.QUEEN: [chess.D1],
                chess.KING: [chess.E1]
            },
            chess.BLACK: {
                chess.KNIGHT: [chess.B8, chess.G8],
                chess.BISHOP: [chess.C8, chess.F8],
                chess.ROOK: [chess.A8, chess.H8],
                chess.QUEEN: [chess.D8],
                chess.KING: [chess.E8]
            }
        }
        
        if (piece.piece_type in starting_squares[piece.color] and
            move.to_square in starting_squares[piece.color][piece.piece_type]):
            score += 4
        
        # Worsening pawn structure
        if piece.piece_type == chess.PAWN:
            self.board.push(move)
            
            # Check for doubled pawns
            file = chess.square_file(move.to_square)
            pawn_count = 0
            for rank in range(8):
                square = chess.square(file, rank)
                square_piece = self.board.piece_at(square)
                if (square_piece and 
                    square_piece.piece_type == chess.PAWN and
                    square_piece.color == piece.color):
                    pawn_count += 1
            
            if pawn_count > 1:
                score += 2
            
            # Check for isolated pawns
            adjacent_files = [f for f in [file-1, file+1] if 0 <= f < 8]
            has_adjacent_pawn = False
            for adj_file in adjacent_files:
                for rank in range(8):
                    square = chess.square(adj_file, rank)
                    square_piece = self.board.piece_at(square)
                    if (square_piece and 
                        square_piece.piece_type == chess.PAWN and
                        square_piece.color == piece.color):
                        has_adjacent_pawn = True
                        break
                if has_adjacent_pawn:
                    break
            
            if not has_adjacent_pawn:
                score += 2
            
            self.board.pop()
        
        # Putting pieces on squares where they can be easily attacked
        self.board.push(move)
        if self.board.is_attacked_by(not piece.color, move.to_square):
            # Check if the piece is defended
            if not self.board.is_attacked_by(piece.color, move.to_square):
                score += 3  # Undefended piece on attacked square
            else:
                score += 1  # Defended but still on attacked square
        self.board.pop()
        
        return score


if __name__ == "__main__":
    run_engine(AntiPositionalEngine)