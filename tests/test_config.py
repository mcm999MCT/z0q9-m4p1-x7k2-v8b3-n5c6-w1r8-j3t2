"""Tests for app/config.py"""

import os

import pytest

from app.config import Config


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Make sure each test starts with a clean set of environment
    variables, so tests don't affect each other or depend on whatever
    happens to be set on the machine running them.
    """
    keys = [
        "SOLANA_RPC_URL",
        "ETHEREUM_RPC_URL",
        "BASE_RPC_URL",
        "BNB_RPC_URL",
        "ARBITRUM_RPC_URL",
        "ROBINHOOD_RPC_URL",
        "DISCORD_WEBHOOK_URL",
        "MARKET_DATA_API_KEY",
        "DATABASE_PATH",
        "SCAN_INTERVAL_SECONDS",
        "ALERT_SCORE_THRESHOLD",
        "MAX_TOKENS_PER_CHAIN",
        "MAX_CONCURRENT_REQUESTS",
        "LOG_LEVEL",
        "DRY_RUN",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    yield


def test_defaults_are_used_when_nothing_is_set():
    config = Config.load()

    assert config.database_path == "data/crypto_bot.db"
    assert config.scan_interval_seconds == 60
    assert config.alert_score_threshold == 80
    assert config.max_tokens_per_chain == 100
    assert config.max_concurrent_requests == 10
    assert config.log_level == "INFO"
    assert config.dry_run is True


def test_missing_optional_values_are_reported():
    config = Config.load()

    # None of the RPC URLs, webhook, or API key are set in this test,
    # so they should all show up as "missing but optional".
    missing_names = [item.split(" ")[0] for item in config.missing_optional]

    assert "SOLANA_RPC_URL" in missing_names
    assert "DISCORD_WEBHOOK_URL" in missing_names
    assert "MARKET_DATA_API_KEY" in missing_names


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("SCAN_INTERVAL_SECONDS", "120")
    monkeypatch.setenv("ALERT_SCORE_THRESHOLD", "90")
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_PATH", "somewhere/else.db")

    config = Config.load()

    assert config.scan_interval_seconds == 120
    assert config.alert_score_threshold == 90
    assert config.dry_run is False
    assert config.log_level == "DEBUG"
    assert config.database_path == "somewhere/else.db"


def test_invalid_integer_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("SCAN_INTERVAL_SECONDS", "not-a-number")

    config = Config.load()

    # Should not crash — should fall back to the documented default.
    assert config.scan_interval_seconds == 60


def test_rpc_urls_are_picked_up_when_set(monkeypatch):
    monkeypatch.setenv("SOLANA_RPC_URL", "https://example.com/solana")
    monkeypatch.setenv("ETHEREUM_RPC_URL", "https://example.com/ethereum")

    config = Config.load()

    assert config.solana_rpc_url == "https://example.com/solana"
    assert config.ethereum_rpc_url == "https://example.com/ethereum"
    # Still not set:
    assert config.base_rpc_url is None


def test_ensure_database_directory_creates_folder(tmp_path):
    config = Config.load()
    config.database_path = str(tmp_path / "nested" / "folder" / "bot.db")

    db_path = config.ensure_database_directory()

    assert db_path.parent.exists()
    assert str(db_path) == config.database_path


def test_summary_does_not_crash_and_is_a_string():
    config = Config.load()
    summary = config.summary()

    assert isinstance(summary, str)
    assert "Configuration summary" in summary
