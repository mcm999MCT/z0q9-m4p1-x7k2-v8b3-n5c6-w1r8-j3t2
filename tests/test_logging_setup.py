"""Tests for app/logging_setup.py

These specifically guard against two mistakes:
1. An actual secret VALUE being logged (must be redacted).
2. A harmless message that merely mentions a setting's NAME being
   incorrectly hidden (must NOT be redacted) — this was a real bug found
   during Stage 1 testing.
"""

import logging

from app.logging_setup import RedactSensitiveFilter


def _apply_filter(message: str) -> str:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )
    RedactSensitiveFilter().filter(record)
    return record.getMessage()


def test_actual_secret_value_is_redacted():
    result = _apply_filter("DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/12345/abcdef")
    assert "discord.com" not in result
    assert "withheld" in result


def test_actual_api_key_value_is_redacted():
    result = _apply_filter("api_key: sk-abcdef1234567890")
    assert "sk-abcdef1234567890" not in result
    assert "withheld" in result


def test_mentioning_a_setting_name_is_not_redacted():
    # This is the exact bug found during Stage 1 manual testing: this
    # message just explains that a setting is missing, with no real value.
    message = "MARKET_DATA_API_KEY — needed for market data lookups"
    result = _apply_filter(message)
    assert result == message


def test_mentioning_missing_discord_webhook_is_not_redacted():
    message = "DISCORD_WEBHOOK_URL — needed to send Discord alerts"
    result = _apply_filter(message)
    assert result == message
