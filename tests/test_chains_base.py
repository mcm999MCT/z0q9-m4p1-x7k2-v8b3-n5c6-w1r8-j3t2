"""Tests for app/chains/base.py"""

import pytest

from app.chains.base import BlockchainProvider, ChainHealth, HealthStatus
from app.models.chain import Chain


def test_blockchain_provider_cannot_be_instantiated_directly():
    # It's an abstract base class — only concrete subclasses (built in
    # Stage 3/4) should be instantiable.
    with pytest.raises(TypeError):
        BlockchainProvider(Chain.SOLANA)  # type: ignore[abstract]


class _DummyHealthyProvider(BlockchainProvider):
    """A minimal fake provider, used only to test the interface shape.
    Not a real chain connection."""

    async def check_health(self) -> ChainHealth:
        return ChainHealth(chain=self.chain, status=HealthStatus.OK)


class _DummyBrokenProvider(BlockchainProvider):
    async def check_health(self) -> ChainHealth:
        return ChainHealth(
            chain=self.chain,
            status=HealthStatus.ERROR,
            message="Simulated connection failure",
        )


@pytest.mark.asyncio
async def test_concrete_subclass_can_report_healthy_status():
    provider = _DummyHealthyProvider(Chain.SOLANA)
    health = await provider.check_health()

    assert health.chain == Chain.SOLANA
    assert health.status == HealthStatus.OK
    assert health.is_ok is True


@pytest.mark.asyncio
async def test_concrete_subclass_can_report_broken_status_with_message():
    provider = _DummyBrokenProvider(Chain.BASE)
    health = await provider.check_health()

    assert health.chain == Chain.BASE
    assert health.status == HealthStatus.ERROR
    assert health.is_ok is False
    assert health.message == "Simulated connection failure"


def test_provider_stores_its_chain():
    provider = _DummyHealthyProvider(Chain.ETHEREUM)
    assert provider.chain == Chain.ETHEREUM
