"""
Collection of weak chess engines for testing and analysis.
"""

from .random_engine import RandomEngine
from .blunder_engine import BlunderEngine
from .greedy_capture_engine import GreedyCaptureEngine
from .shuffle_engine import ShuffleEngine
from .anti_positional_engine import AntiPositionalEngine
from .alphabetical_engine import AlphabeticalEngine
from .reverse_alphabetical_engine import ReverseAlphabeticalEngine

__all__ = [
    'RandomEngine',
    'BlunderEngine', 
    'GreedyCaptureEngine',
    'ShuffleEngine',
    'AntiPositionalEngine',
    'AlphabeticalEngine',
    'ReverseAlphabeticalEngine'
]