"""Tests for app/chains/registry.py"""

import pytest

from app.chains import registry
from app.chains.base import BlockchainProvider, ChainHealth, HealthStatus
from app.models.chain import Chain


@pytest.fixture(autouse=True)
def clean_registry():
    """Each test gets a clean provider registry, so tests registering a
    dummy provider don't leak into other tests."""
    original = dict(registry._PROVIDER_REGISTRY)
    registry._PROVIDER_REGISTRY.clear()
    yield
    registry._PROVIDER_REGISTRY.clear()
    registry._PROVIDER_REGISTRY.update(original)


class _DummyProvider(BlockchainProvider):
    async def check_health(self) -> ChainHealth:
        return ChainHealth(chain=self.chain, status=HealthStatus.OK)


class _NotAProvider:
    """Deliberately NOT a BlockchainProvider subclass, to test validation."""

    pass


def test_no_providers_registered_by_default_in_stage_2():
    # Stage 2 builds the registry mechanism, but Solana/EVM providers don't
    # exist yet — nothing should be registered.
    assert registry.available_chains() == []
    for chain in registry.supported_chains():
        assert registry.is_provider_available(chain) is False


def test_getting_an_unregistered_provider_raises_clear_error():
    with pytest.raises(NotImplementedError, match="solana"):
        registry.get_provider_class(Chain.SOLANA)


def test_supported_chains_lists_all_six_chains():
    chains = registry.supported_chains()
    assert len(chains) == 6
    assert Chain.SOLANA in chains
    assert Chain.ROBINHOOD in chains


def test_register_and_retrieve_a_provider():
    registry.register_provider(Chain.SOLANA, _DummyProvider)

    assert registry.is_provider_available(Chain.SOLANA) is True
    assert registry.get_provider_class(Chain.SOLANA) is _DummyProvider
    assert Chain.SOLANA in registry.available_chains()


def test_registering_a_non_provider_class_is_rejected():
    with pytest.raises(TypeError):
        registry.register_provider(Chain.SOLANA, _NotAProvider)  # type: ignore[arg-type]


def test_registering_one_chain_does_not_affect_others():
    registry.register_provider(Chain.SOLANA, _DummyProvider)

    assert registry.is_provider_available(Chain.SOLANA) is True
    assert registry.is_provider_available(Chain.ETHEREUM) is False
