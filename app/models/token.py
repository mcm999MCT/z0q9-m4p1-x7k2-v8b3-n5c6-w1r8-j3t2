"""
Token models for the Crypto Intelligence Bot.

PROJECT_SPEC.md section 6 ("Chain Identity") requires that a token is never
identified by its address alone — the same address can exist as a completely
different token on different chains. The unique identity must always be:

    (chain, token_address)

This module defines that identity type, plus a lightweight `Token` model
that wraps it with a couple of basic descriptive fields. Full market-data
fields (price, liquidity, volume, etc. — PROJECT_SPEC.md section 10) are
deliberately NOT included yet; those arrive in Stage 5 once a real
market-data provider is chosen, so we don't build a model for data we can't
populate yet (see AGENTS.md rule 6 — never invent data).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.chain import Chain, is_evm_chain


def normalize_address(chain: Chain, address: str) -> str:
    """Normalize a token/wallet address for consistent identity comparison.

    - Whitespace is always trimmed.
    - EVM addresses are case-insensitive at the protocol level, so they are
      lowercased for identity purposes (this only affects how we compare/
      store the address internally — it does not change what the address
      "is").
    - Solana addresses are base58 and ARE case-sensitive, so they are left
      exactly as given (only trimmed).

    Full format validation (e.g. confirming an EVM address is a valid
    40-character hex string, or a Solana address is valid base58) is
    intentionally left for Stage 3/4, once each chain's real provider is
    built — this function only handles identity normalization.
    """
    cleaned = address.strip()
    if not cleaned:
        raise ValueError("Address cannot be empty.")

    if is_evm_chain(chain):
        return cleaned.lower()
    return cleaned


@dataclass(frozen=True)
class TokenIdentity:
    """The unique identity of a token: (chain, token_address).

    Frozen + using normalized fields means two TokenIdentity objects for the
    "same" token will always be equal and hash the same way, so they can
    safely be used as dictionary keys or in sets (important for the
    database and de-duplication logic in later stages).
    """

    chain: Chain
    token_address: str

    def __post_init__(self) -> None:
        normalized = normalize_address(self.chain, self.token_address)
        # Using object.__setattr__ because the dataclass is frozen.
        object.__setattr__(self, "token_address", normalized)

    def __str__(self) -> str:
        return f"({self.chain.value}, {self.token_address})"


@dataclass(frozen=True)
class Token:
    """A token, identified by (chain, token_address), with a couple of
    basic descriptive fields.

    `symbol` and `name` are optional because we may discover a token before
    we have market data for it. Use None (not "UNKNOWN" or an empty
    string) when a value truly isn't known yet, per AGENTS.md rule 6.
    """

    identity: TokenIdentity
    symbol: Optional[str] = None
    name: Optional[str] = None

    @property
    def chain(self) -> Chain:
        return self.identity.chain

    @property
    def token_address(self) -> str:
        return self.identity.token_address
