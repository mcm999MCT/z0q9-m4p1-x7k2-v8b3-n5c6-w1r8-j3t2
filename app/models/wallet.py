"""
Wallet models for the Crypto Intelligence Bot.

PROJECT_SPEC.md section 7 ("Wallet Identity") requires the same rule as
token identity: never identify a wallet by its address alone. The unique
identity must always be:

    (chain, wallet_address)

Section 7 also explicitly warns: do not automatically assume that the same
address on two different EVM chains represents "the same" wallet for
scoring purposes. This module keeps identities chain-scoped so that never
happens by accident — merging wallet intelligence across chains would have
to be a deliberate, explicit decision made elsewhere (a possible future
feature per AGENTS.md rule 12), not something that falls out of how the
identity type works.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.chain import Chain
from app.models.token import normalize_address


@dataclass(frozen=True)
class WalletIdentity:
    """The unique identity of a wallet: (chain, wallet_address).

    Frozen + normalized fields mean two WalletIdentity objects for the
    "same" wallet on the same chain will always be equal and hash the same
    way. A wallet with the same address on two different chains is treated
    as two distinct identities, by design (PROJECT_SPEC.md section 7).
    """

    chain: Chain
    wallet_address: str

    def __post_init__(self) -> None:
        normalized = normalize_address(self.chain, self.wallet_address)
        object.__setattr__(self, "wallet_address", normalized)

    def __str__(self) -> str:
        return f"({self.chain.value}, {self.wallet_address})"
