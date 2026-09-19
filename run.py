#!/usr/bin/env python3
"""
Entry point for the Crypto Intelligence Bot.

Usage:
    python run.py                Normal mode
    python run.py --dry-run      Run without sending real Discord alerts
    python run.py --demo         Run using safe demo/test data where appropriate
    python run.py --once         Perform one scan and exit
"""

import sys

from app.main import run

if __name__ == "__main__":
    sys.exit(run())
