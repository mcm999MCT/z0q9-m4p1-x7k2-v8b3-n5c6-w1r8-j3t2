"""
Chain model for the Crypto Intelligence Bot.

This is the single source of truth for "which blockchains does this bot
support, and what are their identifying details". Every other part of the
application should refer to chains through the `Chain` enum defined here,
rather than using raw strings like "solana" or "ethereum" scattered around
the code.

Chain IDs below come directly from PROJECT_SPEC.md section 4. Solana is not
an EVM chain, so it has no numeric chain ID (chain_id is None).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Chain(str, Enum):
    """The blockchains this bot supports (PROJECT_SPEC.md section 4)."""

    SOLANA = "solana"
    ETHEREUM = "ethereum"
    BASE = "base"
    BNB = "bnb"
    ARBITRUM = "arbitrum"
    ROBINHOOD = "robinhood"


@dataclass(frozen=True)
class ChainInfo:
    """Static, descriptive information about one supported chain.

    This does NOT include any live connection details (like an RPC URL) —
    those come from configuration (app/config.py) and are handled by the
    real chain providers built in Stage 3 (Solana) and Stage 4 (EVM).
    """

    chain: Chain
    display_name: str
    chain_id: Optional[int]  # None for Solana; a real EVM chain ID otherwise
    is_evm: bool


# The complete registry of supported chains and their details.
# Chain IDs are taken directly from PROJECT_SPEC.md section 4 — not invented.
CHAIN_INFO: Dict[Chain, ChainInfo] = {
    Chain.SOLANA: ChainInfo(
        chain=Chain.SOLANA,
        display_name="Solana",
        chain_id=None,
        is_evm=False,
    ),
    Chain.ETHEREUM: ChainInfo(
        chain=Chain.ETHEREUM,
        display_name="Ethereum",
        chain_id=1,
        is_evm=True,
    ),
    Chain.BASE: ChainInfo(
        chain=Chain.BASE,
        display_name="Base",
        chain_id=8453,
        is_evm=True,
    ),
    Chain.BNB: ChainInfo(
        chain=Chain.BNB,
        display_name="BNB Smart Chain",
        chain_id=56,
        is_evm=True,
    ),
    Chain.ARBITRUM: ChainInfo(
        chain=Chain.ARBITRUM,
        display_name="Arbitrum One",
        chain_id=42161,
        is_evm=True,
    ),
    Chain.ROBINHOOD: ChainInfo(
        chain=Chain.ROBINHOOD,
        display_name="Robinhood Chain",
        chain_id=4663,
        is_evm=True,
    ),
}


def all_chains() -> List[Chain]:
    """Return every supported chain, in a stable order."""
    return list(CHAIN_INFO.keys())


def get_chain_info(chain: Chain) -> ChainInfo:
    """Look up the static details for a chain.

    Raises KeyError with a clear message if the chain isn't registered —
    this should never happen for a valid Chain enum member, but fails
    loudly rather than silently if it ever does.
    """
    try:
        return CHAIN_INFO[chain]
    except KeyError as exc:
        raise KeyError(f"Unknown chain: {chain!r}") from exc


def is_evm_chain(chain: Chain) -> bool:
    """True if this chain uses the EVM (Ethereum Virtual Machine) — i.e. it
    can share the common EVMProvider implementation (PROJECT_SPEC.md
    section 4)."""
    return get_chain_info(chain).is_evm


def chain_from_id(chain_id: int) -> Optional[Chain]:
    """Look up which EVM chain a numeric chain ID belongs to.

    Returns None if no supported chain matches (this includes Solana,
    which has no numeric chain ID).
    """
    for chain, info in CHAIN_INFO.items():
        if info.chain_id == chain_id:
            return chain
    return None
