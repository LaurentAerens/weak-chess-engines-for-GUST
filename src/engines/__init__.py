"""
Collection of weak chess engines for testing and analysis.
"""

from .random_engine import RandomEngine
from .alphabetical_engine import AlphabeticalEngine
from .reverse_alphabetical_engine import ReverseAlphabeticalEngine
from .pi_engine import PiEngine
from .euler_engine import EulerEngine
from .suicide_king_engine import SuicideKingEngine
from .blunder_engine import BlunderEngine
from .greedy_capture_engine import GreedyCaptureEngine
from .shuffle_engine import ShuffleEngine
from .anti_positional_engine import AntiPositionalEngine
from .color_square_engine import ColorSquareEngine
from .opposite_color_square_engine import OppositeColorSquareEngine
from .huddle_engine import HuddleEngine
from .swarm_engine import SwarmEngine
from .runaway_engine import RunawayEngine
from .mirror_y_engine import MirrorYEngine
from .mirror_x_engine import MirrorXEngine
from .CCCP_engine import CCCPEngine
from .reverse_start_engine import ReverseStartEngine
from .single_player_engine import SinglePlayerEngine
from .strangler_engine import StranglerEngine
from .mover_engine import MoverEngine
from .opening_book_engine import OpeningBookEngine
from .rare_opening_book_engine import RareOpeningBookEngine
from .lawyer_engine import LawyerEngine
from .criminal_engine import CriminalEngine
from .paralegal_engine import ParalegalEngine

__all__ = [
    'RandomEngine',
    'AlphabeticalEngine',
    'ReverseAlphabeticalEngine',
    'PiEngine',
    'EulerEngine',
    'SuicideKingEngine',
    'BlunderEngine',
    'GreedyCaptureEngine',
    'ShuffleEngine',
    'AntiPositionalEngine',
    'ColorSquareEngine',
    'OppositeColorSquareEngine',
    'SwarmEngine',
    'HuddleEngine',
    'RunawayEngine',
    'MirrorYEngine',
    'MirrorXEngine',
    'ReverseStartEngine',
    'CCCPEngine',
    'PassafistEngine',
    'SinglePlayerEngine',
    'StranglerEngine',
    'MoverEngine',
    'OpeningBookEngine',
    'RareOpeningBookEngine',
    'LawyerEngine',
    'CriminalEngine',
    'ParalegalEngine'
]