#!/usr/bin/env python3
"""
Main GUI application for playing against weak chess engines.
Uses tkinter for the interface and python-chess for game logic.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Dict, Any
import chess
import chess.svg

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from engines.random_engine import RandomEngine
    from engines.blunder_engine import BlunderEngine
    from engines.greedy_capture_engine import GreedyCaptureEngine
    from engines.shuffle_engine import ShuffleEngine
    from engines.anti_positional_engine import AntiPositionalEngine
    from engines.alphabetical_engine import AlphabeticalEngine
    from engines.reverse_alphabetical_engine import ReverseAlphabeticalEngine
    from engines.pi_engine import PiEngine
    from engines.euler_engine import EulerEngine
    from engines.suicide_king_engine import SuicideKingEngine
    from engines.color_square_engine import ColorSquareEngine
    from engines.opposite_color_square_engine import OppositeColorSquareEngine
    from engines.swarm_engine import SwarmEngine
    from engines.huddle_engine import HuddleEngine
    from engines.runaway_engine import RunawayEngine

except ImportError as e:
    print(f"Error importing engines: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class ChessBoard(tk.Frame):
    """Simple chess board GUI using Unicode chess pieces."""
    
    def __init__(self, parent, on_move_callback=None):
        super().__init__(parent)
        self.on_move_callback = on_move_callback
        self.board = chess.Board()
        self.selected_square = None
        self.squares = {}
        self.last_move = None
        
        # Unicode chess pieces
        self.pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        
        self.create_board()
        self.update_display()
    
    def create_board(self):
        """Create the chess board GUI."""
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, 7 - rank)  # Flip rank for display
                
                # Determine square color
                is_light = (rank + file) % 2 == 0
                bg_color = "#F0D9B5" if is_light else "#B58863"
                
                # Create button for each square
                btn = tk.Button(
                    self,
                    width=4,
                    height=2,
                    bg=bg_color,
                    relief='flat',
                    font=('Arial', 20),
                    command=lambda s=square: self.on_square_click(s)
                )
                btn.grid(row=rank, column=file, padx=1, pady=1)
                self.squares[square] = btn
    
    def on_square_click(self, square):
        """Handle square clicks for move input."""
        if self.selected_square is None:
            # First click - select piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.highlight_square(square, "#FFD700")  # Gold highlight
                # Show possible moves
                self.show_legal_moves(square)
        else:
            # Second click - try to make move
            move = self.find_legal_move(self.selected_square, square)
            
            if move and move in self.board.legal_moves:
                self.last_move = move
                self.board.push(move)
                self.update_display()
                if self.on_move_callback:
                    self.on_move_callback()
            
            # Clear selection
            self.clear_highlights()
            self.selected_square = None
    
    def find_legal_move(self, from_square, to_square):
        """Find the correct legal move between two squares, handling special cases."""
        # Check all legal moves from the source square
        for move in self.board.legal_moves:
            if move.from_square == from_square and move.to_square == to_square:
                return move
        
        # If no exact match, try to handle promotion
        piece = self.board.piece_at(from_square)
        if (piece and piece.piece_type == chess.PAWN):
            # Check if this is a promotion move
            if (to_square >= chess.A8 and to_square <= chess.H8) or (to_square >= chess.A1 and to_square <= chess.H1):
                # Try promotion to queen first (most common)
                for promotion_piece in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    move = chess.Move(from_square, to_square, promotion=promotion_piece)
                    if move in self.board.legal_moves:
                        return move
        
        return None
    
    def show_legal_moves(self, from_square):
        """Highlight squares where the selected piece can move."""
        for move in self.board.legal_moves:
            if move.from_square == from_square:
                self.highlight_square(move.to_square, "#90EE90")  # Light green for legal moves
    
    def highlight_square(self, square, color):
        """Highlight a square with the given color."""
        self.squares[square].config(bg=color)
    
    def clear_highlights(self):
        """Clear all square highlights."""
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, 7 - rank)
                is_light = (rank + file) % 2 == 0
                bg_color = "#F0D9B5" if is_light else "#B58863"
                self.squares[square].config(bg=bg_color)
    
    def update_display(self):
        """Update the board display with current position."""
        self.clear_highlights()
        
        # Highlight last move
        if self.last_move:
            self.highlight_square(self.last_move.from_square, "#FFFF99")  # Light yellow
            self.highlight_square(self.last_move.to_square, "#FFFF99")    # Light yellow
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            piece_symbol = ""
            if piece:
                piece_char = piece.symbol()
                piece_symbol = self.pieces.get(piece_char, piece_char)
            
            self.squares[square].config(text=piece_symbol)
        
        # Re-highlight selected square if any
        if self.selected_square is not None:
            self.highlight_square(self.selected_square, "#FFD700")
            self.show_legal_moves(self.selected_square)
    
    def make_move(self, move):
        """Make a move on the board (for engine moves)."""
        if move in self.board.legal_moves:
            self.last_move = move
            self.board.push(move)
            self.update_display()
            return True
        return False
    
    def reset_board(self):
        """Reset the board to starting position."""
        self.board = chess.Board()
        self.selected_square = None
        self.last_move = None
        self.update_display()


class EngineSelector(tk.Frame):
    """Engine selection and configuration panel."""
    
    def __init__(self, parent, on_engine_change=None):
        super().__init__(parent)
        self.on_engine_change = on_engine_change
        
        self.engines = {
            "Huddle Engine (⭐⭐⭐⭐⭐)": HuddleEngine,
            "Random Engine (⭐⭐⭐⭐⭐)": RandomEngine,
            "Alphabetical Engine (⭐⭐⭐⭐)": AlphabeticalEngine,
            "Reverse Alphabetical (⭐⭐⭐⭐)": ReverseAlphabeticalEngine,
            "Pi Engine (⭐⭐⭐⭐)": PiEngine,
            "Euler Engine (⭐⭐⭐⭐)": EulerEngine,
            "Suicide King (⭐⭐⭐⭐)": SuicideKingEngine,
            "Blunder Engine (⭐⭐⭐⭐)": BlunderEngine,
            "Color Square (⭐⭐⭐⭐)": ColorSquareEngine,
            "Opposite Color (⭐⭐⭐⭐)": OppositeColorSquareEngine,
            "Greedy Capture (⭐⭐⭐)": GreedyCaptureEngine,
            "Shuffle Engine (⭐⭐⭐)": ShuffleEngine,
            "Runaway Engine (⭐⭐⭐)": RunawayEngine,
            "Anti-Positional (⭐⭐)": AntiPositionalEngine,
            "Swarm Engine (⭐⭐)": SwarmEngine
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the engine selection widgets."""
        # Engine selection
        tk.Label(self, text="Select Engine:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.engine_var = tk.StringVar()
        self.engine_combo = ttk.Combobox(
            self,
            textvariable=self.engine_var,
            values=list(self.engines.keys()),
            state="readonly",
            width=30
        )
        self.engine_combo.pack(pady=5)
        self.engine_combo.bind('<<ComboboxSelected>>', self.on_selection_change)
        
        # Default selection
        self.engine_combo.current(0)
        
        # Engine info
        self.info_text = tk.Text(
            self,
            height=8,
            width=40,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Arial', 10)
        )
        self.info_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.update_engine_info()
    
    def on_selection_change(self, event=None):
        """Handle engine selection change."""
        self.update_engine_info()
        if self.on_engine_change:
            self.on_engine_change()
    
    def update_engine_info(self):
        """Update the engine information display."""
        selected = self.engine_var.get()
        
        info_texts = {
            "Huddle Engine (⭐⭐⭐⭐⭐)": 
                "The ultimate defensive engine!\n\n"
                "• Prioritizes king safety above all\n"
                "• Forms a protective barrier with pieces\n"
                "• Avoids unnecessary risks\n"
                "• Great for learning defensive strategies\n"
                "• Can be frustrating to play against",

            "Random Engine (⭐⭐⭐⭐⭐)": 
                "The weakest possible engine!\n\n"
                "• Plays completely random legal moves\n"
                "• No planning or evaluation\n"
                "• Pure chaos on the board\n"
                "• Great for absolute beginners\n"
                "• Will hang pieces immediately",
            
            "Alphabetical Engine (⭐⭐⭐⭐)": 
                "The most predictable engine!\n\n"
                "• Always picks first move alphabetically\n"
                "• Completely predictable patterns\n"
                "• Sorts moves by algebraic notation\n"
                "• Great for learning move notation\n"
                "• Easy to exploit once you know the pattern",
            
            "Reverse Alphabetical (⭐⭐⭐⭐)": 
                "Predictably backwards!\n\n"
                "• Always picks last move alphabetically\n"
                "• Prefers 'z' moves over 'a' moves\n"
                "• Opposite pattern to Alphabetical Engine\n"
                "• Still completely predictable\n"
                "• Great for testing pattern recognition",
            
            "Pi Engine (⭐⭐⭐⭐)": 
                "Mathematical constant player!\n\n"
                "• Uses Pi (3.14159...) to pick moves\n"
                "• Maps Pi's fractional part to move index\n"
                "• Semi-predictable but mathematically elegant\n"
                "• Picks ~14% through the move list\n"
                "• Educational and quirky!",
            
            "Euler Engine (⭐⭐⭐⭐)": 
                "Euler's number strategist!\n\n"
                "• Uses e (2.71828...) to pick moves\n"
                "• Maps e's fractional part to move index\n"
                "• Different pattern from Pi Engine\n"
                "• Picks ~72% through the move list\n"
                "• For math enthusiasts!",
            
            "Suicide King (⭐⭐⭐⭐)": 
                "The kamikaze monarch!\n\n"
                "• Tries to move king toward enemy king\n"
                "• Recklessly advances into danger\n"
                "• Ignores safety completely\n"
                "• Great for practicing king attacks\n"
                "• Hilarious and aggressive",
            
            "Blunder Engine (⭐⭐⭐⭐)": 
                "Actively tries to play badly!\n\n"
                "• Evaluates positions to find worst moves\n"
                "• Deliberately hangs pieces\n"
                "• Loves tactical blunders\n"
                "• Makes your chess look brilliant\n"
                "• Educational for learning tactics",

            "Color Square (⭐⭐⭐⭐)": 
                "The color square strategist!\n\n"
                "• Prioritizes control of color squares\n"
                "• Develops pieces to dominate key squares\n"
                "• Ignores material for positional play\n"
                "• Great for learning color complex concepts\n"
                "• Subtle and sophisticated",

            "Opposite Color Square (⭐⭐⭐⭐)": 
                "The opposite color square strategist!\n\n"
                "• Moves pieces onto squares of the opposite color\n"  
                "• Ignores material for positional play\n"
                "• Great for learning color complex concepts\n"
                "• Subtle and sophisticated",

            "Greedy Capture (⭐⭐⭐)": 
                "Material obsessed engine!\n\n"
                "• Always captures when possible\n"
                "• Ignores positional considerations\n"
                "• Tunnel vision for pieces\n"
                "• Weak to tactical traps\n"
                "• Good for practicing tactics",
            
            "Shuffle Engine (⭐⭐⭐)": 
                "The time waster!\n\n"
                "• Moves pieces back and forth\n"
                "• No sense of progress\n"
                "• Wastes tempo constantly\n"
                "• Creates repetitive patterns\n"
                "• Tests your patience",

            "Runaway Engine (⭐⭐⭐)":
                "The fleeing pieces!\n\n"
                "• King runs away from any enemy piece\n"
                "• Prioritizes escape over all else\n"
                "• Ignores other pieces completely\n"
                "• Great for learning evasion tactics\n"
                "• Can be unpredictable and frustrating",

            "Anti-Positional (⭐⭐)": 
                "Violates all chess principles!\n\n"
                "• Avoids central control\n"
                "• Develops pieces poorly\n"
                "• Blocks own pawns\n"
                "• Understands tactics but ignores strategy\n"
                "• Strongest of the weak engines",

            "Swarm Engine (⭐⭐)": 
                "• Pieces move as far away from their own king as possible!\n\n"
                "• Prioritizes distance from own king\n"
                "• Ignores all other considerations\n"
                "• Creates chaotic positions\n"
                "• Can result in aggressive offensive play\n"
                "• Unpredictable and difficult to counter\n"

        }
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_texts.get(selected, "Select an engine for information."))
        self.info_text.config(state=tk.DISABLED)
    
    def get_selected_engine(self):
        """Get the currently selected engine class."""
        selected = self.engine_var.get()
        return self.engines.get(selected, RandomEngine)


class GameControl(tk.Frame):
    """Game control panel with buttons and status."""
    
    def __init__(self, parent, on_new_game=None, on_hint=None):
        super().__init__(parent)
        self.on_new_game = on_new_game
        self.on_hint = on_hint
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the control widgets."""
        # Game control buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="New Game",
            command=self.on_new_game,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Get Hint",
            command=self.on_hint,
            font=('Arial', 12),
            bg='#2196F3',
            fg='white',
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Status display
        tk.Label(self, text="Game Status:", font=('Arial', 11, 'bold')).pack(pady=(20, 5))
        
        self.status_text = tk.Text(
            self,
            height=4,
            width=40,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Arial', 10)
        )
        self.status_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        self.update_status("Welcome! Start a new game to begin.")
        
        # Add instructions
        instructions = tk.Label(
            self,
            text="💡 How to play:\n• Click a piece to select it\n• Green squares show legal moves\n• Yellow squares show the last move\n• Castling works by clicking King → Target square",
            font=('Arial', 9),
            justify=tk.LEFT,
            fg='#666666'
        )
        instructions.pack(pady=5, padx=10)
    
    def update_status(self, message):
        """Update the status display."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, message)
        self.status_text.config(state=tk.DISABLED)


class ChessGUI:
    """Main chess application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weak Chess Engines - Play Against AI")
        self.root.resizable(True, True)
        
        self.engine = None
        self.engine_thinking = False
        self.player_color = chess.WHITE
        
        self.create_widgets()
        self.new_game()
    
    def create_widgets(self):
        """Create the main application widgets."""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - chess board
        left_panel = tk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(left_panel, text="Chess Board", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        self.chess_board = ChessBoard(left_panel, on_move_callback=self.on_player_move)
        self.chess_board.pack()
        
        # Right panel - controls
        right_panel = tk.Frame(main_frame, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_panel.pack_propagate(False)
        
        # Engine selector
        tk.Label(right_panel, text="Engine Selection", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        self.engine_selector = EngineSelector(right_panel, on_engine_change=self.on_engine_change)
        self.engine_selector.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Game controls
        self.game_control = GameControl(
            right_panel,
            on_new_game=self.new_game,
            on_hint=self.get_hint
        )
        self.game_control.pack(fill=tk.BOTH, expand=True)
    
    def on_engine_change(self):
        """Handle engine selection change."""
        if not self.engine_thinking:
            self.new_game()
    
    def new_game(self):
        """Start a new game."""
        if self.engine_thinking:
            messagebox.showwarning("Game in Progress", "Please wait for the engine to finish thinking.")
            return
        
        # Create new engine instance
        engine_class = self.engine_selector.get_selected_engine()
        self.engine = engine_class()
        
        # Reset board
        self.chess_board.reset_board()
        
        # Update status
        self.game_control.update_status(
            f"New game started!\n"
            f"You are White, {self.engine.name} is Black.\n"
            f"Make your move!"
        )
        
        # If engine plays white, make first move
        if self.player_color == chess.BLACK:
            self.make_engine_move()
    
    def on_player_move(self):
        """Handle player move completion."""
        if self.chess_board.board.is_game_over():
            self.handle_game_over()
            return
        
        # Engine's turn
        self.make_engine_move()
    
    def make_engine_move(self):
        """Make the engine move in a separate thread."""
        if self.engine_thinking:
            return
        
        self.engine_thinking = True
        self.game_control.update_status(f"{self.engine.name} is thinking...")
        
        # Start engine thinking in separate thread
        threading.Thread(target=self._engine_move_thread, daemon=True).start()
    
    def _engine_move_thread(self):
        """Engine move thread function."""
        try:
            # Update engine board state
            self.engine.board = self.chess_board.board.copy()
            
            # Get engine move
            move = self.engine.get_best_move(1.0)  # 1 second thinking time
            
            if move and move in self.chess_board.board.legal_moves:
                # Schedule move execution on main thread
                self.root.after(0, self._execute_engine_move, move)
            else:
                self.root.after(0, self._handle_engine_error)
                
        except Exception as e:
            self.root.after(0, self._handle_engine_error, str(e))
    
    def _execute_engine_move(self, move):
        """Execute engine move on main thread."""
        self.chess_board.make_move(move)
        self.engine_thinking = False
        
        # Update status
        move_str = f"{chess.square_name(move.from_square)}-{chess.square_name(move.to_square)}"
        self.game_control.update_status(f"{self.engine.name} played: {move_str}\nYour turn!")
        
        # Check for game over
        if self.chess_board.board.is_game_over():
            self.handle_game_over()
    
    def _handle_engine_error(self, error_msg="Unknown error"):
        """Handle engine errors."""
        self.engine_thinking = False
        self.game_control.update_status(f"Engine error: {error_msg}\nTry starting a new game.")
    
    def handle_game_over(self):
        """Handle game over conditions."""
        board = self.chess_board.board
        
        if board.is_checkmate():
            winner = "You" if not board.turn else self.engine.name
            result_msg = f"Checkmate! {winner} won!"
        elif board.is_stalemate():
            result_msg = "Stalemate! It's a draw."
        elif board.is_insufficient_material():
            result_msg = "Draw by insufficient material."
        elif board.is_fivefold_repetition():
            result_msg = "Draw by repetition."
        else:
            result_msg = "Game over."
        
        self.game_control.update_status(f"{result_msg}\nStart a new game to play again.")
        messagebox.showinfo("Game Over", result_msg)
    
    def get_hint(self):
        """Provide a hint for the current position."""
        if self.engine_thinking:
            messagebox.showwarning("Please Wait", "Engine is currently thinking.")
            return
        
        if self.chess_board.board.is_game_over():
            messagebox.showinfo("Game Over", "The game is already finished.")
            return
        
        # Use the random engine to suggest a move (ironic hint!)
        hint_engine = RandomEngine()
        hint_engine.board = self.chess_board.board.copy()
        
        try:
            hint_move = hint_engine.get_best_move(0.5)
            if hint_move:
                from_square = chess.square_name(hint_move.from_square)
                to_square = chess.square_name(hint_move.to_square)
                piece = self.chess_board.board.piece_at(hint_move.from_square)
                piece_name = piece.name if piece else "piece"
                
                hint_text = f"Random suggestion:\nMove {piece_name} from {from_square} to {to_square}"
                messagebox.showinfo("Hint", hint_text)
            else:
                messagebox.showinfo("Hint", "No move suggestions available.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate hint: {e}")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = ChessGUI()
        app.run()
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nMake sure you have installed the required dependencies:")
        print("pip install chess")
        print("\nAnd that you're running from the project root directory.")
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()