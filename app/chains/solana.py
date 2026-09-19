"""
Solana blockchain provider for the Crypto Intelligence Bot.

This is the first REAL blockchain connection in the project. It talks to a
Solana JSON-RPC endpoint (configured via SOLANA_RPC_URL — never hard-coded)
using only official, documented RPC methods, verified against
https://solana.com/docs/rpc/http/ before writing any code here (per
AGENTS.md rule 7):

    getHealth               — is the RPC node reachable and healthy?
    getTokenSupply           — total supply of an SPL token
    getTokenLargestAccounts  — the 20 largest holders of an SPL token

This is Stage 3 scope only: read-only connectivity and basic token lookups.
Nothing here trades, signs transactions, or touches a private key — this
provider cannot do those things even in principle, since it never accepts
a wallet's private key or seed phrase as input (AGENTS.md rules 4 and 5).

IMPORTANT — about the largest holder accounts (PROJECT_SPEC.md section 16):
getTokenLargestAccounts returns the 20 largest *token accounts*, which are
NOT automatically human wallets. They can be liquidity pools, programs,
burn addresses, lockers, or other infrastructure. This module does not
attempt to label them — that labeling work is Stage 7 (Holder analysis).
This module's job is only to fetch the raw, accurate data.
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.chains.base import BlockchainProvider, ChainHealth, HealthStatus
from app.chains.solana_address import is_valid_solana_address
from app.models.chain import Chain

logger = logging.getLogger(__name__)

# Sensible, documented defaults (PROJECT_SPEC.md section 32 requires
# timeouts, retries, and backoff; none of these numbers are secrets, so
# they're plain constants rather than environment variables — the one
# thing that must be configurable per AGENTS.md rule 8/PROJECT_SPEC.md
# section 9 is the RPC URL itself, which callers pass in).
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE_SECONDS = 0.5


class SolanaRpcError(Exception):
    """Raised when a Solana RPC call ultimately fails (after any retries)."""


class _RetryableRpcFailure(Exception):
    """Internal: a failure worth retrying (timeout, rate limit, server error)."""


class _NonRetryableRpcFailure(Exception):
    """Internal: a failure that won't be fixed by retrying (bad request, bad JSON)."""


@dataclass(frozen=True)
class TokenSupply:
    """Normalized result of getTokenSupply.

    `amount` is the raw, base-unit supply as a string (Solana amounts can
    exceed what a standard float can represent exactly, so the raw string
    is kept alongside the human-readable `ui_amount`).
    """

    token_address: str
    amount: str
    decimals: int
    ui_amount: Optional[float]


@dataclass(frozen=True)
class TokenHolderAccount:
    """One entry from getTokenLargestAccounts.

    NOT automatically a human wallet — see PROJECT_SPEC.md section 16.
    Labeling (liquidity pool, program, burn address, etc.) is a Stage 7
    concern, not this one.
    """

    address: str
    amount: str
    decimals: int
    ui_amount: Optional[float]


@dataclass(frozen=True)
class TokenLargestAccounts:
    """The full result of a getTokenLargestAccounts call for one token."""

    token_address: str
    accounts: List[TokenHolderAccount]


class SolanaProvider(BlockchainProvider):
    """Read-only connection to a Solana JSON-RPC endpoint.

    This class implements the BlockchainProvider interface from Stage 2.
    It only ever reads public blockchain data — it has no method that
    accepts a private key, seed phrase, or that could sign or submit a
    transaction.
    """

    def __init__(
        self,
        rpc_url: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base_seconds: float = DEFAULT_BACKOFF_BASE_SECONDS,
    ) -> None:
        super().__init__(Chain.SOLANA)

        if not rpc_url or not rpc_url.strip():
            raise ValueError(
                "SolanaProvider requires a non-empty rpc_url. "
                "Set SOLANA_RPC_URL in your .env file — see .env.example."
            )
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1.")

        self.rpc_url = rpc_url.strip()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds

    @classmethod
    def from_config(cls, config: "app.config.Config") -> "SolanaProvider":  # type: ignore[name-defined]
        """Convenience constructor for later stages: build a SolanaProvider
        straight from the application's Config object.

        Raises a clear error if SOLANA_RPC_URL hasn't been set.
        """
        if not config.solana_rpc_url:
            raise ValueError(
                "Cannot create a SolanaProvider: SOLANA_RPC_URL is not set. "
                "Add it to your .env file (see .env.example)."
            )
        return cls(rpc_url=config.solana_rpc_url)

    # ------------------------------------------------------------------
    # Low-level JSON-RPC plumbing
    # ------------------------------------------------------------------

    def _post_sync(self, method: str, params: List[Any]) -> Dict[str, Any]:
        """Make one blocking HTTP JSON-RPC request. Runs inside a worker
        thread (see `_call`) so it doesn't block the event loop.

        Raises _RetryableRpcFailure for problems worth retrying (timeouts,
        rate limits, server errors), or _NonRetryableRpcFailure for
        problems that retrying won't fix (bad request, malformed
        response).
        """
        payload = json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        ).encode("utf-8")

        request = urllib.request.Request(
            self.rpc_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            # 429 = rate limited, 5xx = server-side problem — both are
            # worth retrying. Other 4xx codes mean our request itself was
            # bad, so retrying won't help.
            if exc.code == 429 or exc.code >= 500:
                raise _RetryableRpcFailure(f"HTTP {exc.code}: {exc.reason}") from exc
            raise _NonRetryableRpcFailure(f"HTTP {exc.code}: {exc.reason}") from exc
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            # Covers connection refused, DNS failures, and timeouts.
            reason = getattr(exc, "reason", exc)
            raise _RetryableRpcFailure(str(reason)) from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise _NonRetryableRpcFailure(f"Invalid JSON in RPC response: {exc}") from exc

    async def _call(self, method: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Make a JSON-RPC call with timeout handling, retries, and
        exponential backoff (PROJECT_SPEC.md section 32).

        Raises SolanaRpcError if the call ultimately fails, or if the RPC
        node itself returns a JSON-RPC error response. Never raises any
        other exception type.
        """
        params = params or []
        last_error: Optional[BaseException] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await asyncio.to_thread(self._post_sync, method, params)
            except _RetryableRpcFailure as exc:
                last_error = exc
                if attempt < self.max_retries:
                    delay = self.backoff_base_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        "Solana RPC '%s' failed (attempt %s/%s): %s. Retrying in %.1fs.",
                        method, attempt, self.max_retries, exc, delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise SolanaRpcError(
                    f"Solana RPC '{method}' failed after {self.max_retries} attempts: {exc}"
                ) from exc
            except _NonRetryableRpcFailure as exc:
                raise SolanaRpcError(f"Solana RPC '{method}' failed: {exc}") from exc
            else:
                if "error" in response:
                    error_detail = response["error"]
                    message = (
                        error_detail.get("message", str(error_detail))
                        if isinstance(error_detail, dict)
                        else str(error_detail)
                    )
                    raise SolanaRpcError(f"Solana RPC '{method}' returned an error: {message}")
                return response

        # Defensive fallback; the loop above always returns or raises.
        raise SolanaRpcError(
            f"Solana RPC '{method}' failed after {self.max_retries} attempts: {last_error}"
        )

    # ------------------------------------------------------------------
    # BlockchainProvider interface
    # ------------------------------------------------------------------

    async def check_health(self) -> ChainHealth:
        """Check whether the configured Solana RPC endpoint is reachable
        and healthy, using the official getHealth method.

        Never raises — any problem becomes a ChainHealth with status
        ERROR and an explanatory message, per the BlockchainProvider
        contract from Stage 2.
        """
        try:
            response = await self._call("getHealth")
        except SolanaRpcError as exc:
            return ChainHealth(chain=self.chain, status=HealthStatus.ERROR, message=str(exc))

        result = response.get("result")
        if result == "ok":
            return ChainHealth(chain=self.chain, status=HealthStatus.OK)

        return ChainHealth(
            chain=self.chain,
            status=HealthStatus.ERROR,
            message=f"Unexpected getHealth result: {result!r}",
        )

    # ------------------------------------------------------------------
    # Basic token lookups (PROJECT_SPEC.md section 16)
    # ------------------------------------------------------------------

    async def get_token_supply(self, token_address: str) -> Optional[TokenSupply]:
        """Get the total supply of an SPL token, using getTokenSupply.

        Returns None (and logs a warning) if the address isn't a
        plausible Solana address, if the RPC call fails after retries, or
        if the node has no data for it — per AGENTS.md rule 6, this NEVER
        invents a value; unavailable data stays unavailable.
        """
        if not is_valid_solana_address(token_address):
            logger.warning(
                "get_token_supply: %r is not a valid-looking Solana address; skipping.",
                token_address,
            )
            return None

        try:
            response = await self._call("getTokenSupply", [token_address])
        except SolanaRpcError as exc:
            logger.warning("get_token_supply failed for %s: %s", token_address, exc)
            return None

        value = (response.get("result") or {}).get("value")
        if value is None:
            return None

        return TokenSupply(
            token_address=token_address,
            amount=value.get("amount", "0"),
            decimals=value.get("decimals", 0),
            ui_amount=value.get("uiAmount"),
        )

    async def get_token_largest_accounts(
        self, token_address: str, limit: Optional[int] = None
    ) -> Optional[TokenLargestAccounts]:
        """Get the largest holder accounts of an SPL token, using
        getTokenLargestAccounts (returns up to the top 20 by protocol
        design; pass `limit` to trim that further if you want fewer).

        Returns None on invalid address or RPC failure, for the same
        reasons as get_token_supply above.

        Reminder: these are token ACCOUNTS, not confirmed human wallets.
        """
        if not is_valid_solana_address(token_address):
            logger.warning(
                "get_token_largest_accounts: %r is not a valid-looking Solana address; skipping.",
                token_address,
            )
            return None

        try:
            response = await self._call("getTokenLargestAccounts", [token_address])
        except SolanaRpcError as exc:
            logger.warning("get_token_largest_accounts failed for %s: %s", token_address, exc)
            return None

        value = (response.get("result") or {}).get("value")
        if value is None:
            return None

        accounts = [
            TokenHolderAccount(
                address=entry["address"],
                amount=entry.get("amount", "0"),
                decimals=entry.get("decimals", 0),
                ui_amount=entry.get("uiAmount"),
            )
            for entry in value
        ]
        if limit is not None:
            accounts = accounts[:limit]

        return TokenLargestAccounts(token_address=token_address, accounts=accounts)
