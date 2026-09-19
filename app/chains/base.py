"""
Blockchain provider interface for the Crypto Intelligence Bot.

PROJECT_SPEC.md section 5 calls for a common blockchain interface, so the
rest of the application doesn't need to know the low-level details of each
chain:

    BlockchainProvider
            |
    SolanaProvider   EVMProvider

Stage 2 scope: only the shared "shape" is defined here — an abstract base
class that any real provider must follow. There is NO real blockchain
connection code in this file. The concrete SolanaProvider arrives in
Stage 3, and EVMProvider (shared by Ethereum, Base, BNB, Arbitrum, and
Robinhood — PROJECT_SPEC.md section 4) arrives in Stage 4.

Design note on scope: only `check_health()` is required by this interface
so far. That's deliberately the minimum needed to support PROJECT_SPEC.md
section 19 / 31 ("one chain failing must not stop the entire application").
Additional abstract methods (e.g. reading token supply, holder data,
security checks) will be added to this interface only once each
capability is actually built against verified, official documentation
(AGENTS.md rule 7) — not guessed at now. This keeps the interface honest:
every method on it will always correspond to something a provider can
really do.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.models.chain import Chain


class HealthStatus(str, Enum):
    """Whether a provider can currently reach its data source."""

    OK = "OK"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ChainHealth:
    """The result of checking whether a chain's provider is reachable.

    Used by the future scanner (Stage 12) to implement PROJECT_SPEC.md
    section 19's requirement that one chain failing (e.g. Base) must not
    stop the others from being scanned:

        Solana       OK
        Ethereum     OK
        Base         ERROR
        BNB          OK
    """

    chain: Chain
    status: HealthStatus
    message: Optional[str] = None

    @property
    def is_ok(self) -> bool:
        return self.status == HealthStatus.OK


class BlockchainProvider(ABC):
    """Abstract base class every chain-specific provider must implement.

    A concrete provider (SolanaProvider in Stage 3, EVMProvider in Stage 4)
    wraps up all the chain-specific details (RPC calls, response formats,
    quirks) behind this common shape, so the rest of the bot can treat
    every chain the same way.
    """

    def __init__(self, chain: Chain) -> None:
        self.chain = chain

    @abstractmethod
    async def check_health(self) -> ChainHealth:
        """Check whether this provider can currently reach its data source
        (e.g. an RPC endpoint).

        Implementations must NEVER raise an exception from this method —
        any connection problem should be caught and returned as a
        ChainHealth with status ERROR and an explanatory message instead.
        This is what allows one broken chain to be skipped without
        crashing the whole scanner.
        """
        raise NotImplementedError
