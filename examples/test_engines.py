#!/usr/bin/env python3
"""
Example script showing how to test the engines programmatically.
This demonstrates engine vs engine games and basic UCI communication.
"""

import sys
import os
import chess
import chess.engine
import time
from typing import Optional, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engines.random_engine import RandomEngine
from engines.alphabetical_engine import AlphabeticalEngine
from engines.reverse_alphabetical_engine import ReverseAlphabeticalEngine
from engines.pi_engine import PiEngine
from engines.euler_engine import EulerEngine
from engines.suicide_king_engine import SuicideKingEngine
from engines.blunder_engine import BlunderEngine
from engines.greedy_capture_engine import GreedyCaptureEngine
from engines.shuffle_engine import ShuffleEngine
from engines.anti_positional_engine import AntiPositionalEngine
from engines.color_square_engine import ColorSquareEngine
from engines.opposite_color_square_engine import OppositeColorSquareEngine
from engines.runaway_engine import RunawayEngine
from engines.swarm_engine import SwarmEngine
from engines.huddle_engine import HuddleEngine
from engines.mirror_y_engine import MirrorYEngine
from engines.mirror_x_engine import MirrorXEngine


class EngineGame:
    """Simple engine vs engine game simulator."""
    
    def __init__(self, white_engine, black_engine, max_moves=100):
        self.white_engine = white_engine
        self.black_engine = black_engine
        self.board = chess.Board()
        self.max_moves = max_moves
        self.moves = []
    
    def play_game(self, time_per_move=1.0):
        """Play a complete game between two engines."""
        print(f"Game: {self.white_engine.name} (White) vs {self.black_engine.name} (Black)")
        print("=" * 60)
        
        move_count = 0
        
        while not self.board.is_game_over() and move_count < self.max_moves:
            # Choose the current engine
            current_engine = self.white_engine if self.board.turn else self.black_engine
            color = "White" if self.board.turn else "Black"
            
            # Get the move
            start_time = time.time()
            move = current_engine.get_best_move(time_per_move)
            think_time = time.time() - start_time
            
            if move is None or move not in self.board.legal_moves:
                print(f"ERROR: {current_engine.name} ({color}) made illegal move: {move}")
                break
            
            # Make the move
            self.board.push(move)
            self.moves.append(move)
            move_count += 1
            
            # Display move
            print(f"{move_count:2d}. {color:5s}: {move:5s} ({think_time:.3f}s)")
            
            # Update engine boards
            self.white_engine.board = self.board.copy()
            self.black_engine.board = self.board.copy()
        
        # Game result
        print("\n" + "=" * 60)
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            print(f"Game Over: {winner} wins by checkmate!")
        elif self.board.is_stalemate():
            print("Game Over: Stalemate!")
        elif self.board.is_insufficient_material():
            print("Game Over: Insufficient material!")
        elif move_count >= self.max_moves:
            print(f"Game Over: Maximum moves ({self.max_moves}) reached!")
        else:
            print("Game Over: Unknown reason")
        
        print(f"Final position: {self.board.fen()}")
        print(f"Total moves: {len(self.moves)}")
        return self.board.result()


def test_engine_basics():
    """Test basic engine functionality."""
    print("Testing Engine Basics")
    print("=" * 40)
    
    engines = [
        RandomEngine(),
        AlphabeticalEngine(),
        ReverseAlphabeticalEngine(),
        PiEngine(),
        EulerEngine(),
        SuicideKingEngine(),
        BlunderEngine(),
        GreedyCaptureEngine(),
        ShuffleEngine(),
        AntiPositionalEngine(),
        ColorSquareEngine(),
        OppositeColorSquareEngine(),
        SwarmEngine(),
        HuddleEngine(),
        RunawayEngine(),
        MirrorYEngine(),
        MirrorXEngine()
    ]
    
    for engine in engines:
        print(f"\nTesting {engine.name}:")
        
        # Test from starting position
        engine.board = chess.Board()
        move = engine.get_best_move(0.1)
        
        if move and move in engine.board.legal_moves:
            print(f"  ✓ Generated legal move: {move}")
        else:
            print(f"  ✗ Failed to generate legal move: {move}")
        
        # Test from a middle game position
        engine.board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4")
        move = engine.get_best_move(0.1)
        
        if move and move in engine.board.legal_moves:
            print(f"  ✓ Generated legal move from complex position: {move}")
        else:
            print(f"  ✗ Failed in complex position: {move}")


def tournament():
    """Run a small tournament between engines."""
    print("\nWeak Engine Tournament")
    print("=" * 40)
    
    engines = [
        RandomEngine(),
        AlphabeticalEngine(),
        ReverseAlphabeticalEngine(),
        PiEngine(),
        EulerEngine(),
        SuicideKingEngine(),
        BlunderEngine(),
        GreedyCaptureEngine(),
        ShuffleEngine(),
        AntiPositionalEngine(),
        ColorSquareEngine(),
        OppositeColorSquareEngine()
    ]
    
    results = {}
    for engine in engines:
        results[engine.name] = {'wins': 0, 'losses': 0, 'draws': 0}
    
    games_played = 0
    total_games = len(engines) * (len(engines) - 1)  # Each pair plays once
    
    for i, white_engine in enumerate(engines):
        for j, black_engine in enumerate(engines):
            if i != j:  # Don't play against self
                games_played += 1
                print(f"\nGame {games_played}/{total_games}")
                
                game = EngineGame(white_engine, black_engine, max_moves=50)
                result = game.play_game(time_per_move=0.2)
                
                if result == "1-0":  # White wins
                    results[white_engine.name]['wins'] += 1
                    results[black_engine.name]['losses'] += 1
                elif result == "0-1":  # Black wins
                    results[black_engine.name]['wins'] += 1
                    results[white_engine.name]['losses'] += 1
                else:  # Draw
                    results[white_engine.name]['draws'] += 1
                    results[black_engine.name]['draws'] += 1
    
    # Print tournament results
    print("\n" + "=" * 60)
    print("TOURNAMENT RESULTS")
    print("=" * 60)
    print(f"{'Engine':<25} {'Wins':<6} {'Losses':<6} {'Draws':<6} {'Score':<6}")
    print("-" * 60)
    
    for engine_name, stats in results.items():
        total_games = stats['wins'] + stats['losses'] + stats['draws']
        score = stats['wins'] + 0.5 * stats['draws']
        print(f"{engine_name:<25} {stats['wins']:<6} {stats['losses']:<6} {stats['draws']:<6} {score:<6.1f}")


def demonstrate_uci():
    """Demonstrate UCI protocol communication."""
    print("\nUCI Protocol Demonstration")
    print("=" * 40)
    
    engine = RandomEngine()
    
    print("Simulating UCI commands:")
    print("→ uci")
    engine.handle_uci()
    
    print("\n→ isready")
    engine.handle_isready()
    
    print("\n→ position startpos moves e2e4 e7e5")
    engine.handle_position(['startpos', 'moves', 'e2e4', 'e7e5'])
    print(f"Board after moves: {engine.board.fen()}")
    
    print("\n→ go movetime 1000")
    move = engine.get_best_move(1.0)
    print(f"bestmove {move}")


if __name__ == "__main__":
    print("Weak Chess Engines - Test Suite")
    print("=" * 50)
    
    try:
        # Run basic tests
        test_engine_basics()
        
        # Demonstrate UCI
        demonstrate_uci()
        
        # Ask user if they want to run tournament
        print("\n" + "=" * 50)
        response = input("Run tournament? (y/N): ").lower().strip()
        
        if response in ['y', 'yes']:
            tournament()
        else:
            print("Skipping tournament.")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest suite completed!")