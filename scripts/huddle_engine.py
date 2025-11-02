#!/usr/bin/env python3
"""
UCI entry point for Huddle Engine
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from engines.huddle_engine import HuddleEngine
from base_engine import run_engine

if __name__ == "__main__":
    run_engine(HuddleEngine)
