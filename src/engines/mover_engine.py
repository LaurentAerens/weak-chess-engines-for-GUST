import chess
import random
from base_engine import BaseUCIEngine

class MoverEngine(BaseUCIEngine):
    def __init__(self):
        super().__init__("Mover", "Laurent Aerens")
        # stable piece ids: map current square -> piece_id for our pieces
        self.piece_id_by_square = {}  # square -> id
        self.next_piece_id = 1
        # move counts keyed by piece_id
        self.piece_move_counts = {}  # piece_id -> move count
        # square visit counts keyed by square
        self.square_visit_counts = {}  # square -> visit count

    def get_best_move(self, think_time: float = 1.0):
        board = self.board
        # Rebuild ids and counts from full move history so earlier moves (made by any side) are counted
        self._rebuild_from_move_stack(board)
        # Sync piece_id_by_square for our color: add missing pieces and remove captured ones
        our_color = board.turn
        current_piece_map = {sq: p for sq, p in board.piece_map().items() if p.color == our_color}

        # Remove any tracked ids for squares that no longer have our piece
        to_remove = [sq for sq in self.piece_id_by_square if sq not in current_piece_map]
        for sq in to_remove:
            pid = self.piece_id_by_square.pop(sq, None)
            # we keep historical counts for pid (don't delete)

        # Add tracking for any of our pieces not yet seen
        for sq in current_piece_map:
            if sq not in self.piece_id_by_square:
                pid = self.next_piece_id
                self.next_piece_id += 1
                self.piece_id_by_square[sq] = pid
                self.piece_move_counts.setdefault(pid, 0)

        # Ensure square visit counts keys exist (don't change counts yet)
        for sq in chess.SQUARES:
            if board.piece_at(sq):
                self.square_visit_counts.setdefault(sq, 0)
        # Find move stats
        move_stats = []
        for move in board.legal_moves:
            piece_square = move.from_square
            # look up piece id; if missing assign one (covers promotions or newly seen pieces)
            pid = self.piece_id_by_square.get(piece_square)
            if pid is None:
                pid = self.next_piece_id
                self.next_piece_id += 1
                self.piece_id_by_square[piece_square] = pid
                self.piece_move_counts.setdefault(pid, 0)

            piece_count = self.piece_move_counts.get(pid, 0)
            dest_count = self.square_visit_counts.get(move.to_square, 0)
            move_stats.append((piece_count, dest_count, move, pid))
        # Find moves with min piece_count
        if not move_stats:
            return None
        min_piece = min(ms[0] for ms in move_stats)
        moves_min_piece = [ms for ms in move_stats if ms[0] == min_piece]
        min_dest = min(ms[1] for ms in moves_min_piece)
        best_moves = [ms for ms in moves_min_piece if ms[1] == min_dest]
        chosen_piece_count, chosen_dest_count, chosen_move, chosen_pid = random.choice(best_moves)
        # Update stats: move the pid mapping to the destination square
        # Remove old mapping (if exists)
        old_sq = chosen_move.from_square
        if old_sq in self.piece_id_by_square:
            self.piece_id_by_square.pop(old_sq, None)
        # Assign pid to new square
        self.piece_id_by_square[chosen_move.to_square] = chosen_pid
        # Increment the move count for this piece id and visit count for destination
        self.piece_move_counts[chosen_pid] = self.piece_move_counts.get(chosen_pid, 0) + 1
        self.square_visit_counts[chosen_move.to_square] = self.square_visit_counts.get(chosen_move.to_square, 0) + 1
        return chosen_move

    def _rebuild_from_move_stack(self, board):
        """Reconstruct piece ids and move counts by replaying moves from the initial position for this board."""
        # Create a temporary copy and pop all moves to reach the starting position
        temp = board.copy()
        moves = list(temp.move_stack)
        # Undo all moves on temp to get the start position
        while temp.move_stack:
            temp.pop()

        # Reset mappings
        self.piece_id_by_square = {}
        self.piece_move_counts = {}
        self.next_piece_id = 1

        # Assign ids to pieces in the starting position
        for sq, piece in temp.piece_map().items():
            pid = self.next_piece_id
            self.next_piece_id += 1
            self.piece_id_by_square[sq] = pid
            self.piece_move_counts[pid] = 0

        # Replay moves and update mappings and counts
        for mv in moves:
            # mv is a chess.Move with from_square and to_square
            from_sq = mv.from_square
            to_sq = mv.to_square

            pid = self.piece_id_by_square.get(from_sq)
            if pid is None:
                # Assign if missing (shouldn't normally happen)
                pid = self.next_piece_id
                self.next_piece_id += 1
                self.piece_move_counts.setdefault(pid, 0)

            # increment move count for the piece that moved
            self.piece_move_counts[pid] = self.piece_move_counts.get(pid, 0) + 1

            # Handle captures: remove any pid mapped to destination (captured piece)
            if to_sq in self.piece_id_by_square:
                # captured pid removed
                self.piece_id_by_square.pop(to_sq, None)

            # Move pid mapping from from_sq to to_sq
            self.piece_id_by_square.pop(from_sq, None)
            self.piece_id_by_square[to_sq] = pid
