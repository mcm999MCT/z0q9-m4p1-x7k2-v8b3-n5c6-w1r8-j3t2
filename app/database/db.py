"""
Database connection and schema setup for the Crypto Intelligence Bot.

Stage 1 scope:
    This module only sets up the SQLite database file and a small
    "schema_meta" table that records which schema version is installed.

    The real tables described in PROJECT_SPEC.md section 30
    (chains, tokens, token_observations, holders, wallets,
    wallet_transactions, wallet_token_positions, token_scores, alerts)
    will be added incrementally in later stages, as each feature is built.
    This keeps changes small and easy to test, per AGENTS.md rule #23
    ("do not rewrite working code unnecessarily") and rule #3
    ("build incrementally").

Using SQLite because:
    - It's free.
    - It's a single file — no server to install or pay for.
    - It's well supported by Python's standard library.
    (See AGENTS.md rule #21 and PROJECT_SPEC.md section 30.)
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# Bump this number whenever the schema changes in a future stage.
CURRENT_SCHEMA_VERSION = 1


def get_connection(database_path: Union[str, Path]) -> sqlite3.Connection:
    """Open (and if necessary create) the SQLite database file, and return
    a connection to it.
    """
    db_path = Path(database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(db_path))
    # Return rows that behave like dictionaries (access columns by name),
    # which makes the code that uses this connection much easier to read.
    connection.row_factory = sqlite3.Row

    # Enforce foreign key constraints (off by default in SQLite).
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(database_path: Union[str, Path]) -> sqlite3.Connection:
    """Create the database file if it doesn't exist yet, and make sure the
    schema-tracking table is present. Returns an open connection.

    This function is safe to call every time the application starts:
    it will not erase or duplicate existing data.
    """
    connection = get_connection(database_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_meta (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            schema_version INTEGER NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    existing = connection.execute(
        "SELECT schema_version FROM schema_meta WHERE id = 1"
    ).fetchone()

    if existing is None:
        connection.execute(
            "INSERT INTO schema_meta (id, schema_version) VALUES (1, ?)",
            (CURRENT_SCHEMA_VERSION,),
        )
        connection.commit()
        logger.info(
            "Initialized new database at %s (schema version %s)",
            database_path,
            CURRENT_SCHEMA_VERSION,
        )
    else:
        logger.info(
            "Database already exists at %s (schema version %s)",
            database_path,
            existing["schema_version"],
        )

    return connection


def get_schema_version(connection: sqlite3.Connection) -> int:
    """Read the currently installed schema version from the database."""
    row = connection.execute(
        "SELECT schema_version FROM schema_meta WHERE id = 1"
    ).fetchone()
    if row is None:
        raise RuntimeError(
            "Database has not been initialized yet. Call initialize_database() first."
        )
    return row["schema_version"]
