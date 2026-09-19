"""
Main application entry point (called by run.py).

Stage 1 scope:
    Wire together configuration, logging, and the database.
    There is no blockchain scanning yet — that starts in Stage 3 onward.

Later stages will expand `run()` to actually scan chains, analyze tokens,
and send Discord alerts.
"""

from __future__ import annotations

import argparse
import logging

from app.config import Config
from app.database.db import initialize_database
from app.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def parse_args(argv=None) -> argparse.Namespace:
    """Define and parse the command-line flags described in PROJECT_SPEC.md
    section 35 (Operating Modes).
    """
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Crypto Intelligence Bot — multi-chain token & wallet intelligence scanner.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending real Discord alerts.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run using safe demo/test data where appropriate (clearly labeled as demo data).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Perform one scan and exit, instead of running continuously.",
    )
    return parser.parse_args(argv)


def run(argv=None) -> int:
    """Application entry point. Returns a process exit code (0 = success)."""
    args = parse_args(argv)

    # 1. Load configuration from environment variables / .env file.
    config = Config.load()

    # Command-line --dry-run always wins over the DRY_RUN environment
    # variable, so it's easy to force a safe run from the terminal.
    if args.dry_run:
        config.dry_run = True

    # 2. Set up logging as early as possible so everything below is logged.
    setup_logging(config.log_level)

    logger.info("Starting Crypto Intelligence Bot")
    logger.info("Mode flags -> dry_run=%s demo=%s once=%s", config.dry_run, args.demo, args.once)

    if config.missing_optional:
        logger.warning(
            "Some optional configuration values are not set yet. "
            "These are not required for this stage, but will be needed later:"
        )
        for item in config.missing_optional:
            logger.warning("  - %s", item)

    logger.info("\n%s", config.summary())

    # 3. Initialize the database (creates the file/folder and schema-tracking
    #    table if they don't exist yet).
    db_path = config.ensure_database_directory()
    connection = initialize_database(db_path)

    try:
        # Stage 1 has nothing further to do. Future stages will call the
        # scanner service here.
        if args.demo:
            logger.info(
                "[DEMO MODE] No scanning logic exists yet (arrives in later stages). "
                "This flag is recognized and will be wired up when the scanner is built."
            )
        else:
            logger.info(
                "Foundation check complete: configuration, logging, and database "
                "are all working. No scanning logic exists yet — that arrives in "
                "later stages."
            )

        logger.info("Crypto Intelligence Bot finished this run cleanly.")
        return 0
    finally:
        connection.close()
