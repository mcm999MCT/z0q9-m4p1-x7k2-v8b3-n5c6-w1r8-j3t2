"""
Chain registry for the Crypto Intelligence Bot.

This is the lookup table the rest of the application will use to go from
"which chain is this?" to "what provider object talks to that chain?" —
without needing to know anything about Solana vs. EVM details.

Stage 2 scope: the registry mechanism is built and tested here, but NO
providers are registered yet, because SolanaProvider (Stage 3) and
EVMProvider (Stage 4) don't exist yet. Attempting to look up a provider
right now will raise a clear NotImplementedError explaining that it
arrives in a later stage — this is expected and tested behavior, not a
bug.

When Stage 3 and Stage 4 are built, they will call `register_provider()`
to plug their real provider classes in here. This file itself should not
need to change when that happens.
"""

from __future__ import annotations

from typing import Dict, List, Type

from app.chains.base import BlockchainProvider
from app.models.chain import Chain, all_chains

# Maps a chain to the concrete BlockchainProvider subclass that implements
# it. Empty in Stage 2 — filled in by Stage 3 (Solana) and Stage 4 (EVM).
_PROVIDER_REGISTRY: Dict[Chain, Type[BlockchainProvider]] = {}


def register_provider(chain: Chain, provider_class: Type[BlockchainProvider]) -> None:
    """Register the concrete provider class that implements a given chain.

    Called by later stages once a real provider exists. Not called
    anywhere yet in Stage 2.
    """
    if not issubclass(provider_class, BlockchainProvider):
        raise TypeError(
            f"{provider_class!r} must be a subclass of BlockchainProvider."
        )
    _PROVIDER_REGISTRY[chain] = provider_class


def get_provider_class(chain: Chain) -> Type[BlockchainProvider]:
    """Look up the provider class registered for a chain.

    Raises NotImplementedError with a clear, friendly message if no
    provider has been registered for that chain yet (expected for every
    chain during Stage 2, since none are built yet).
    """
    provider_class = _PROVIDER_REGISTRY.get(chain)
    if provider_class is None:
        raise NotImplementedError(
            f"No provider has been implemented yet for chain '{chain.value}'. "
            f"This will be added in a later development stage."
        )
    return provider_class


def is_provider_available(chain: Chain) -> bool:
    """True if a real provider has been registered for this chain."""
    return chain in _PROVIDER_REGISTRY


def supported_chains() -> List[Chain]:
    """Every chain this bot is designed to eventually support (regardless
    of whether a provider has been built for it yet)."""
    return all_chains()


def available_chains() -> List[Chain]:
    """Chains that currently have a working, registered provider. Will be
    an empty list until Stage 3/4 register real providers."""
    return [chain for chain in all_chains() if is_provider_available(chain)]
