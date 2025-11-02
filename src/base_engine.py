"""
Base UCI (Universal Chess Interface) engine implementation.
All weak chess engines inherit from this base class.
"""

import sys
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional
import chess
import chess.engine


class BaseUCIEngine(ABC):
    """Base class for all UCI chess engines."""
    
    def __init__(self, name: str, author: str):
        self.name = name
        self.author = author
        self.board = chess.Board()
        self.thinking = False
        self.stop_thinking = False
        
    def uci_loop(self):
        """Main UCI command loop."""
        while True:
            try:
                line = input().strip()
                if not line:
                    continue
                    
                parts = line.split()
                command = parts[0].lower()
                
                if command == "uci":
                    self.handle_uci()
                elif command == "isready":
                    self.handle_isready()
                elif command == "ucinewgame":
                    self.handle_ucinewgame()
                elif command == "position":
                    self.handle_position(parts[1:])
                elif command == "go":
                    self.handle_go(parts[1:])
                elif command == "stop":
                    self.handle_stop()
                elif command == "quit":
                    break
                    
            except EOFError:
                break
            except Exception as e:
                # Silent error handling for UCI compatibility
                pass
    
    def handle_uci(self):
        """Handle UCI identification."""
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        print("uciok")
        sys.stdout.flush()
    
    def handle_isready(self):
        """Handle ready check."""
        print("readyok")
        sys.stdout.flush()
    
    def handle_ucinewgame(self):
        """Handle new game."""
        self.board = chess.Board()
    
    def handle_position(self, args):
        """Handle position setup."""
        if not args:
            return
            
        if args[0] == "startpos":
            self.board = chess.Board()
            if len(args) > 1 and args[1] == "moves":
                for move_str in args[2:]:
                    try:
                        move = chess.Move.from_uci(move_str)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                    except:
                        pass
        elif args[0] == "fen":
            # Find where moves start
            moves_index = -1
            for i, arg in enumerate(args):
                if arg == "moves":
                    moves_index = i
                    break
            
            if moves_index > 0:
                fen = " ".join(args[1:moves_index])
                try:
                    self.board = chess.Board(fen)
                    # Apply moves after the FEN
                    for move_str in args[moves_index + 1:]:
                        try:
                            move = chess.Move.from_uci(move_str)
                            if move in self.board.legal_moves:
                                self.board.push(move)
                        except:
                            pass
                except:
                    pass
            else:
                # No moves, just FEN
                fen = " ".join(args[1:])
                try:
                    self.board = chess.Board(fen)
                except:
                    pass
    
    def handle_go(self, args):
        """Handle go command."""
        if self.thinking:
            return
            
        self.stop_thinking = False
        
        # Parse time controls (simplified)
        wtime = None
        btime = None
        winc = None
        binc = None
        movestogo = None
        depth = None
        movetime = None
        
        i = 0
        while i < len(args):
            if args[i] == "wtime" and i + 1 < len(args):
                try:
                    wtime = int(args[i + 1])
                except:
                    pass
                i += 2
            elif args[i] == "btime" and i + 1 < len(args):
                try:
                    btime = int(args[i + 1])
                except:
                    pass
                i += 2
            elif args[i] == "winc" and i + 1 < len(args):
                try:
                    winc = int(args[i + 1])
                except:
                    pass
                i += 2
            elif args[i] == "binc" and i + 1 < len(args):
                try:
                    binc = int(args[i + 1])
                except:
                    pass
                i += 2
            elif args[i] == "movestogo" and i + 1 < len(args):
                try:
                    movestogo = int(args[i + 1])
                except:
                    pass
                i += 2
            elif args[i] == "depth" and i + 1 < len(args):
                try:
                    depth = int(args[i + 1])
                except:
                    pass
                i += 2
            elif args[i] == "movetime" and i + 1 < len(args):
                try:
                    movetime = int(args[i + 1])
                except:
                    pass
                i += 2
            else:
                i += 1
        
        # Start thinking in a separate thread
        thinking_thread = threading.Thread(
            target=self._think_and_move,
            args=(wtime, btime, winc, binc, movestogo, depth, movetime)
        )
        thinking_thread.daemon = True
        thinking_thread.start()
    
    def handle_stop(self):
        """Handle stop command."""
        self.stop_thinking = True
    
    def _think_and_move(self, wtime, btime, winc, binc, movestogo, depth, movetime):
        """Think and output the best move."""
        self.thinking = True
        
        try:
            # Calculate thinking time
            if movetime:
                think_time = movetime / 1000.0  # Convert to seconds
            else:
                # Simple time management
                if self.board.turn == chess.WHITE and wtime:
                    base_time = wtime / 1000.0
                elif self.board.turn == chess.BLACK and btime:
                    base_time = btime / 1000.0
                else:
                    base_time = 1.0  # Default 1 second
                
                # Use a fraction of available time
                think_time = min(base_time / 20, 5.0)  # Max 5 seconds, min 1/20 of time
                think_time = max(think_time, 0.1)  # Minimum 0.1 seconds
            
            # Get the move from the engine
            best_move = self.get_best_move(think_time)
            
            if not self.stop_thinking and best_move:
                print(f"bestmove {best_move.uci()}")
                sys.stdout.flush()
                
        except Exception as e:
            # Fallback to random legal move
            legal_moves = list(self.board.legal_moves)
            if legal_moves and not self.stop_thinking:
                import random
                move = random.choice(legal_moves)
                print(f"bestmove {move.uci()}")
                sys.stdout.flush()
        
        self.thinking = False
    
    @abstractmethod
    def get_best_move(self, think_time: float) -> Optional[chess.Move]:
        """
        Get the best move according to this engine.
        
        Args:
            think_time: Maximum time to think in seconds
            
        Returns:
            The best move, or None if no move is found
        """
        pass


def run_engine(engine_class, *args, **kwargs):
    """Run a UCI engine."""
    engine = engine_class(*args, **kwargs)
    engine.uci_loop()