import os
import sys
import subprocess
import chess
import chess.engine
import chess.pgn
from collections import defaultdict

# List of engine classes (imported directly)
from src.engines.random_engine import RandomEngine
from src.engines.alphabetical_engine import AlphabeticalEngine
from src.engines.reverse_alphabetical_engine import ReverseAlphabeticalEngine
from src.engines.pi_engine import PiEngine
from src.engines.euler_engine import EulerEngine
from src.engines.suicide_king_engine import SuicideKingEngine
from src.engines.blunder_engine import BlunderEngine
from src.engines.greedy_capture_engine import GreedyCaptureEngine
from src.engines.shuffle_engine import ShuffleEngine
from src.engines.anti_positional_engine import AntiPositionalEngine

ENGINES = [
    ("Random", RandomEngine),
    ("Alphabetical", AlphabeticalEngine),
    ("Reverse Alphabetical", ReverseAlphabeticalEngine),
    ("Pi", PiEngine),
    ("Euler", EulerEngine),
    ("Suicide King", SuicideKingEngine),
    ("Blunder", BlunderEngine),
    ("Greedy Capture", GreedyCaptureEngine),
    ("Shuffle", ShuffleEngine),
    ("Anti-Positional", AntiPositionalEngine),
]

RESULTS = defaultdict(lambda: {"win": 0, "loss": 0, "draw": 0})

# Tournament settings
MAX_MOVES = 80
TIME_LIMIT = 0.2  # seconds per move



import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

print("Starting round-robin tournament...")

# Store all games for PGN export
all_games = []


# Prepare all matchups
def game_task(white_name, white_class, black_name, black_class):
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["White"] = white_name
    game.headers["Black"] = black_name
    node = game
    try:
        white_engine = white_class()
        black_engine = black_class()
        print(f"\nGame: {white_name} (White) vs {black_name} (Black)")
        for move_num in range(MAX_MOVES):
            if board.is_game_over():
                break
            if board.turn == chess.WHITE:
                white_engine.board = board.copy()
                move = white_engine.get_best_move(TIME_LIMIT)
            else:
                black_engine.board = board.copy()
                move = black_engine.get_best_move(TIME_LIMIT)
            if move is None or move not in board.legal_moves:
                break
            board.push(move)
            node = node.add_variation(move)
        outcome = board.outcome()
        if outcome is None or outcome.result() == "*":
            result_type = "draw"
            game.headers["Result"] = "1/2-1/2"
        elif outcome.winner is None:
            result_type = "draw"
            game.headers["Result"] = "1/2-1/2"
        elif outcome.winner == chess.WHITE:
            result_type = "white_win"
            game.headers["Result"] = "1-0"
        else:
            result_type = "black_win"
            game.headers["Result"] = "0-1"
        print(f"Result: {white_name} (White) vs {black_name} (Black): {game.headers['Result']}")
        return (white_name, black_name, result_type, game)
    except Exception as e:
        print(f"Error running engines: {e}")
        game.headers["Result"] = "1/2-1/2"
        return (white_name, black_name, "draw", game)

tasks = []
for i, (name1, class1) in enumerate(ENGINES):
    for j, (name2, class2) in enumerate(ENGINES):
        if i == j:
            continue
        for color in [chess.WHITE, chess.BLACK]:
            white_name, white_class = (name1, class1) if color == chess.WHITE else (name2, class2)
            black_name, black_class = (name2, class2) if color == chess.WHITE else (name1, class1)
            tasks.append((white_name, white_class, black_name, black_class))

print(f"Starting round-robin tournament with {len(tasks)} games...")

# Run games in parallel (max out system resources)
all_games = []
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(game_task, *args) for args in tasks]
    for future in as_completed(futures):
        white_name, black_name, result_type, game = future.result()
        all_games.append(game)
        if result_type == "white_win":
            RESULTS[white_name]["win"] += 1
            RESULTS[black_name]["loss"] += 1
        elif result_type == "black_win":
            RESULTS[black_name]["win"] += 1
            RESULTS[white_name]["loss"] += 1
        else:
            RESULTS[white_name]["draw"] += 1
            RESULTS[black_name]["draw"] += 1



print("\nTournament complete!\n")
print("Engine Rankings (by points):")

# Calculate points: win=1, draw=0.5, loss=0
engine_points = {}
for name, stats in RESULTS.items():
    points = stats["win"] * 1 + stats["draw"] * 0.5
    engine_points[name] = points

ranking = sorted(RESULTS.items(), key=lambda x: (-engine_points[x[0]], -x[1]["win"], x[1]["loss"]))
for name, stats in ranking:
    points = engine_points[name]
    print(f"{name:20} | Points: {points:5.1f} | Wins: {stats['win']:3} | Losses: {stats['loss']:3} | Draws: {stats['draw']:3}")

# Export results table as CSV (with points)
with open("tournament_results.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Engine", "Points", "Wins", "Losses", "Draws"])
    for name, stats in ranking:
        points = engine_points[name]
        writer.writerow([name, f"{points:.1f}", stats["win"], stats["loss"], stats["draw"]])
print("Results exported to tournament_results.csv")

# Export all games as a single PGN file
with open("tournament_games.pgn", "w") as pgnfile:
    for game in all_games:
        print(game, file=pgnfile, end="\n\n")
print("All games exported to tournament_games.pgn")
