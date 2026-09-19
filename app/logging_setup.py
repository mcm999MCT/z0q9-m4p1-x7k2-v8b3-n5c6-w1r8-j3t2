"""
Logging setup for the Crypto Intelligence Bot.

Keeps logging simple and consistent across the whole application, and makes
sure we never accidentally log secrets (API keys, private keys, passwords,
webhook URLs, etc.) — see AGENTS.md rule #20.
"""

from __future__ import annotations

import logging
import re
import sys

# A backstop against accidentally logging a secret VALUE (not just the
# NAME of a setting). We only redact when a sensitive-looking keyword is
# immediately followed by "=" or ":" and then a non-trivial value, e.g.
#   "DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/..."
#   "api_key: sk-abc123..."
# Simply mentioning a variable's name (e.g. in a "this is not configured
# yet" message) must NOT be redacted, or real diagnostic messages become
# unreadable.
_SENSITIVE_VALUE_PATTERN = re.compile(
    r"(PRIVATE_KEY|SEED_PHRASE|SECRET|PASSWORD|API_KEY|WEBHOOK_URL)\s*[:=]\s*\S{4,}",
    re.IGNORECASE,
)


class RedactSensitiveFilter(logging.Filter):
    """A safety net: if a log message contains what looks like an actual
    secret VALUE (a sensitive keyword directly assigned to something),
    replace the message with a warning instead of leaking it. This is a
    backstop, not a substitute for careful coding — application code
    should never pass secrets into log calls in the first place.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            return True

        if _SENSITIVE_VALUE_PATTERN.search(message):
            record.msg = "[log message withheld: possible sensitive content]"
            record.args = ()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configure root logging for the whole application.

    Call this once, early, when the program starts (see run.py).
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RedactSensitiveFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers if setup_logging() is called more than once
    # (e.g. in tests).
    root_logger.handlers = [handler]
