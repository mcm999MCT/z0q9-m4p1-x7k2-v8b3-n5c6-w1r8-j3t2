"""Tests for app/database/db.py"""

from pathlib import Path

from app.database.db import (
    CURRENT_SCHEMA_VERSION,
    get_connection,
    get_schema_version,
    initialize_database,
)


def test_initialize_database_creates_file_and_folder(tmp_path):
    db_path = tmp_path / "nested" / "crypto_bot.db"
    assert not db_path.exists()

    connection = initialize_database(db_path)
    connection.close()

    assert db_path.exists()


def test_initialize_database_sets_schema_version(tmp_path):
    db_path = tmp_path / "crypto_bot.db"

    connection = initialize_database(db_path)
    version = get_schema_version(connection)
    connection.close()

    assert version == CURRENT_SCHEMA_VERSION


def test_initialize_database_is_safe_to_call_twice(tmp_path):
    db_path = tmp_path / "crypto_bot.db"

    connection1 = initialize_database(db_path)
    connection1.close()

    # Calling it again should not fail, error, or reset the schema version.
    connection2 = initialize_database(db_path)
    version = get_schema_version(connection2)
    connection2.close()

    assert version == CURRENT_SCHEMA_VERSION


def test_get_connection_enables_foreign_keys(tmp_path):
    db_path = tmp_path / "crypto_bot.db"

    connection = get_connection(db_path)
    result = connection.execute("PRAGMA foreign_keys").fetchone()
    connection.close()

    assert result[0] == 1


def test_get_connection_returns_row_objects_accessible_by_name(tmp_path):
    db_path = tmp_path / "crypto_bot.db"

    connection = initialize_database(db_path)
    row = connection.execute(
        "SELECT schema_version FROM schema_meta WHERE id = 1"
    ).fetchone()
    connection.close()

    # sqlite3.Row supports both index and name access
    assert row["schema_version"] == CURRENT_SCHEMA_VERSION
