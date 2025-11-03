# If True, engines will also play against themselves
SELF_PLAY = False
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
from src.engines.color_square_engine import ColorSquareEngine
from src.engines.opposite_color_square_engine import OppositeColorSquareEngine
from src.engines.runaway_engine import RunawayEngine
from src.engines.huddle_engine import HuddleEngine
from src.engines.swarm_engine import SwarmEngine
from src.engines.mirror_y_engine import MirrorYEngine
from src.engines.mirror_x_engine import MirrorXEngine
from src.engines.reverse_start_engine import ReverseStartEngine
from src.engines.CCCP_engine import CCCPEngine
from src.engines.passafist_engine import PassafistEngine
from src.engines.single_player_engine import SinglePlayerEngine
from src.engines.strangler_engine import StranglerEngine
from src.engines.mover_engine import MoverEngine

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
    ("Color Square", ColorSquareEngine),
    ("Opposite Color Square", OppositeColorSquareEngine),
    ("Runaway", RunawayEngine),
    ("Huddle", HuddleEngine),
    ("Swarm", SwarmEngine),
    ("Mirror Y", MirrorYEngine),
    ("Mirror X", MirrorXEngine),
    ("Reverse Start", ReverseStartEngine),
    ("CCCP", CCCPEngine),
    ("Passafist", PassafistEngine),
    ("Single Player", SinglePlayerEngine),
    ("Strangler", StranglerEngine),
    ("Mover", MoverEngine)
]

RESULTS = defaultdict(lambda: {"win": 0, "loss": 0, "draw": 0})
# Pairwise results: (white, black) -> score (+1 white win, 0 draw, -1 black win)
PAIRWISE = {}

# Tournament settings
# No per-move time limit and no maximum move limit - games run until completion



import csv
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed


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
        # Play until the game is over; engines may accept a think_time parameter or not.
        while not board.is_game_over():
            if board.turn == chess.WHITE:
                white_engine.board = board.copy()
                try:
                    move = white_engine.get_best_move()
                except TypeError:
                    # Fallback for engines that still expect a time argument
                    move = white_engine.get_best_move(0)
            else:
                black_engine.board = board.copy()
                try:
                    move = black_engine.get_best_move()
                except TypeError:
                    move = black_engine.get_best_move(0)
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
        return (white_name, black_name, result_type, str(game))
    except Exception as e:
        print(f"Error running engines: {e}")
        game.headers["Result"] = "1/2-1/2"
        return (white_name, black_name, "draw", str(game))

tasks = []
for i, (name1, class1) in enumerate(ENGINES):
    for j, (name2, class2) in enumerate(ENGINES):
        if i == j and not SELF_PLAY:
            continue
        for color in [chess.WHITE, chess.BLACK]:
            white_name, white_class = (name1, class1) if color == chess.WHITE else (name2, class2)
            black_name, black_class = (name2, class2) if color == chess.WHITE else (name1, class1)
            tasks.append((white_name, white_class, black_name, black_class))

# Duplicate tasks for the requested number of rounds
def main():
    parser = argparse.ArgumentParser(description='Run round-robin tournament between weak engines')
    parser.add_argument('--rounds', '-r', type=int, default=1, help='Number of full round-robin rounds to run (default: 1)')
    parser.add_argument('--self-play', type=str, default='false', help='Enable engines to play against themselves (true/false, default: false)')
    parser.add_argument('--workers', '-w', type=int, default=os.cpu_count() or 1, help='Number of worker processes to use (default: all CPUs)')
    args = parser.parse_args()
    ROUNDS = max(1, args.rounds)
    SELF_PLAY = args.self_play.lower() == 'true'
    WORKERS = max(1, args.workers)

    print(f"Starting round-robin tournament... Rounds: {ROUNDS}, Self-play: {SELF_PLAY}, Workers: {WORKERS}")

    # Store all games for PGN export
    all_games = []

    # Prepare task list for all rounds
    all_task_args = [args for _ in range(ROUNDS) for args in tasks]
    print(f"Starting round-robin tournament with {len(all_task_args)} games ({ROUNDS} rounds, {len(tasks)} games per round)...")

    # Run games in parallel using processes
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(game_task, *a) for a in all_task_args]
        for future in as_completed(futures):
            white_name, black_name, result_type, game_pgn = future.result()
            all_games.append(game_pgn)
        # Update aggregate stats
            if result_type == "white_win":
                RESULTS[white_name]["win"] += 1
                RESULTS[black_name]["loss"] += 1
                score = 1
            elif result_type == "black_win":
                RESULTS[black_name]["win"] += 1
                RESULTS[white_name]["loss"] += 1
                score = -1
            else:
                RESULTS[white_name]["draw"] += 1
                RESULTS[black_name]["draw"] += 1
                score = 0

        # For pairwise matrix, if multiple rounds, accumulate by summing scores
        key = (white_name, black_name)
        PAIRWISE[key] = PAIRWISE.get(key, 0) + score


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
        for game_pgn in all_games:
            pgnfile.write(game_pgn + "\n\n")
    print("All games exported to tournament_games.pgn")

    # Print pairwise results matrix (rows = White, columns = Black)
    engine_names = [name for name, _ in ENGINES]

    print('\nPairwise Results (rows = White, columns = Black):')
    header = ['Engine'] + engine_names
    print(' | '.join(header))
    print(' | '.join(['---'] * len(header)))
    for white in engine_names:
        row = [white]
        for black in engine_names:
            if white == black:
                row.append('')
            else:
                val = PAIRWISE.get((white, black), 0)
                row.append(str(val))
        print(' | '.join(row))

    # Export pairwise matrix to CSV
    with open('pairwise_results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([''] + engine_names)
        for white in engine_names:
            row = [white]
            for black in engine_names:
                if white == black:
                    row.append('')
                else:
                    row.append(str(PAIRWISE.get((white, black), 0)))
            writer.writerow(row)
    print('Pairwise results exported to pairwise_results.csv')


if __name__ == "__main__":
    main()
