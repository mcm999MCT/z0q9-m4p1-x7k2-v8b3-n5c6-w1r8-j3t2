"""
Configuration loader for the Crypto Intelligence Bot.

This module reads settings from environment variables (and, if present,
a local .env file) and makes them available to the rest of the application
as a single Config object.

Design rules (per AGENTS.md):
- Never hard-code API keys or secrets.
- Never crash the whole app just because an optional value is missing.
- Clearly report which values are missing so the project owner knows
  what to fix.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    # python-dotenv lets us load a local .env file during development.
    # It is optional: if it's not installed, we simply skip loading .env
    # and rely on real environment variables instead.
    from dotenv import load_dotenv

    _DOTENV_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when dependency missing
    _DOTENV_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_str(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read a string environment variable. Returns default if unset or blank."""
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _get_int(name: str, default: int) -> int:
    """Read an integer environment variable, falling back to default on
    anything invalid (missing, blank, or not a number)."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _get_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable.

    Accepts (case-insensitive): true/false, 1/0, yes/no.
    """
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Config object
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Holds every configuration value the bot needs.

    Values that are required for a specific feature (e.g. an RPC URL for a
    specific chain, or the Discord webhook) are allowed to be empty at this
    stage, because those features are not built yet. Later stages will
    check for the specific values they need, when they need them.
    """

    # --- Blockchain RPC endpoints (used starting Stage 3/4) ---
    solana_rpc_url: Optional[str] = None
    ethereum_rpc_url: Optional[str] = None
    base_rpc_url: Optional[str] = None
    bnb_rpc_url: Optional[str] = None
    arbitrum_rpc_url: Optional[str] = None
    robinhood_rpc_url: Optional[str] = None

    # --- Alerts (used starting Stage 11) ---
    discord_webhook_url: Optional[str] = None

    # --- Market data (used starting Stage 5) ---
    market_data_api_key: Optional[str] = None

    # --- Database ---
    database_path: str = "data/crypto_bot.db"

    # --- Scanner behavior (used starting Stage 6/12) ---
    scan_interval_seconds: int = 60
    alert_score_threshold: int = 80
    max_tokens_per_chain: int = 100
    max_concurrent_requests: int = 10

    # --- General ---
    log_level: str = "INFO"
    dry_run: bool = True

    # Populated automatically: human-readable list of optional values
    # that are currently missing. Nothing breaks because of these; they
    # are just reported so the project owner knows what to add later.
    missing_optional: List[str] = field(default_factory=list)

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables (and .env if present)."""
        if _DOTENV_AVAILABLE:
            # Look for a .env file in the current working directory or any
            # parent directory. Does nothing if no .env file exists.
            load_dotenv()

        cfg = cls(
            solana_rpc_url=_get_str("SOLANA_RPC_URL"),
            ethereum_rpc_url=_get_str("ETHEREUM_RPC_URL"),
            base_rpc_url=_get_str("BASE_RPC_URL"),
            bnb_rpc_url=_get_str("BNB_RPC_URL"),
            arbitrum_rpc_url=_get_str("ARBITRUM_RPC_URL"),
            robinhood_rpc_url=_get_str("ROBINHOOD_RPC_URL"),
            discord_webhook_url=_get_str("DISCORD_WEBHOOK_URL"),
            market_data_api_key=_get_str("MARKET_DATA_API_KEY"),
            database_path=_get_str("DATABASE_PATH", "data/crypto_bot.db"),
            scan_interval_seconds=_get_int("SCAN_INTERVAL_SECONDS", 60),
            alert_score_threshold=_get_int("ALERT_SCORE_THRESHOLD", 80),
            max_tokens_per_chain=_get_int("MAX_TOKENS_PER_CHAIN", 100),
            max_concurrent_requests=_get_int("MAX_CONCURRENT_REQUESTS", 10),
            log_level=_get_str("LOG_LEVEL", "INFO"),
            dry_run=_get_bool("DRY_RUN", True),
        )

        cfg.missing_optional = cfg._find_missing_optional()
        return cfg

    def _find_missing_optional(self) -> List[str]:
        """Return a plain-language list of optional settings that are not
        yet configured. These are not required for Stage 1, but future
        stages will need them.
        """
        checks = [
            ("SOLANA_RPC_URL", self.solana_rpc_url, "needed for Solana scanning"),
            ("ETHEREUM_RPC_URL", self.ethereum_rpc_url, "needed for Ethereum scanning"),
            ("BASE_RPC_URL", self.base_rpc_url, "needed for Base scanning"),
            ("BNB_RPC_URL", self.bnb_rpc_url, "needed for BNB Smart Chain scanning"),
            ("ARBITRUM_RPC_URL", self.arbitrum_rpc_url, "needed for Arbitrum scanning"),
            ("ROBINHOOD_RPC_URL", self.robinhood_rpc_url, "needed for Robinhood Chain scanning"),
            ("DISCORD_WEBHOOK_URL", self.discord_webhook_url, "needed to send Discord alerts"),
            ("MARKET_DATA_API_KEY", self.market_data_api_key, "needed for market data lookups (may not be required depending on provider chosen)"),
        ]
        missing = []
        for env_name, value, reason in checks:
            if value is None:
                missing.append(f"{env_name} — {reason}")
        return missing

    def ensure_database_directory(self) -> Path:
        """Make sure the folder that will hold the SQLite database file exists.
        Returns the resolved Path to the database file.
        """
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    def summary(self) -> str:
        """A short, human-readable summary of the current configuration,
        safe to print or log (never includes secret values themselves)."""
        lines = [
            "Configuration summary:",
            f"  Database path:            {self.database_path}",
            f"  Scan interval (seconds):  {self.scan_interval_seconds}",
            f"  Alert score threshold:    {self.alert_score_threshold}",
            f"  Max tokens per chain:     {self.max_tokens_per_chain}",
            f"  Max concurrent requests:  {self.max_concurrent_requests}",
            f"  Log level:                {self.log_level}",
            f"  Dry run:                  {self.dry_run}",
            "",
            "  RPC endpoints configured:",
            f"    Solana:     {'yes' if self.solana_rpc_url else 'no'}",
            f"    Ethereum:   {'yes' if self.ethereum_rpc_url else 'no'}",
            f"    Base:       {'yes' if self.base_rpc_url else 'no'}",
            f"    BNB:        {'yes' if self.bnb_rpc_url else 'no'}",
            f"    Arbitrum:   {'yes' if self.arbitrum_rpc_url else 'no'}",
            f"    Robinhood:  {'yes' if self.robinhood_rpc_url else 'no'}",
            "",
            f"  Discord webhook configured: {'yes' if self.discord_webhook_url else 'no'}",
            f"  Market data API key set:    {'yes' if self.market_data_api_key else 'no'}",
        ]
        return "\n".join(lines)
