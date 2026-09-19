"""Tests for app/chains/solana.py

No real network calls are made in these tests. The low-level HTTP layer
(urllib.request.urlopen) is mocked so we can test retry/backoff/error
handling behavior deterministically and offline, using response shapes
copied exactly from the official Solana RPC documentation
(https://solana.com/docs/rpc/http/).
"""

import json
import urllib.error

import pytest

from app.chains.base import BlockchainProvider, HealthStatus
from app.chains.solana import (
    SolanaProvider,
    SolanaRpcError,
    TokenLargestAccounts,
    TokenSupply,
)
from app.models.chain import Chain

VALID_RPC_URL = "https://api.mainnet-beta.solana.com"
# A real, well-known Solana address (USDC mint) — used only to satisfy
# format validation. No live lookups are performed.
TOKEN_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


class _FakeHttpResponse:
    """A minimal stand-in for what urllib.request.urlopen() returns."""

    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _rpc_ok(result):
    return json.dumps({"jsonrpc": "2.0", "id": 1, "result": result}).encode("utf-8")


def _rpc_error(code, message):
    return json.dumps(
        {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}
    ).encode("utf-8")


# ----------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------

def test_provider_requires_a_non_empty_rpc_url():
    with pytest.raises(ValueError):
        SolanaProvider(rpc_url="")

    with pytest.raises(ValueError):
        SolanaProvider(rpc_url="   ")


def test_provider_is_a_real_blockchain_provider_subclass():
    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    assert isinstance(provider, BlockchainProvider)
    assert provider.chain == Chain.SOLANA


def test_provider_can_be_registered_in_the_stage_2_registry():
    # Confirms the Stage 2 registry mechanism and the real Stage 3
    # provider actually fit together.
    from app.chains import registry

    original = dict(registry._PROVIDER_REGISTRY)
    try:
        registry.register_provider(Chain.SOLANA, SolanaProvider)
        assert registry.is_provider_available(Chain.SOLANA) is True
        assert registry.get_provider_class(Chain.SOLANA) is SolanaProvider
    finally:
        registry._PROVIDER_REGISTRY.clear()
        registry._PROVIDER_REGISTRY.update(original)


def test_from_config_requires_solana_rpc_url_to_be_set():
    from app.config import Config

    config = Config.load()
    config.solana_rpc_url = None

    with pytest.raises(ValueError, match="SOLANA_RPC_URL"):
        SolanaProvider.from_config(config)


def test_from_config_builds_a_working_provider(monkeypatch):
    from app.config import Config

    monkeypatch.setenv("SOLANA_RPC_URL", VALID_RPC_URL)
    config = Config.load()

    provider = SolanaProvider.from_config(config)
    assert provider.rpc_url == VALID_RPC_URL


# ----------------------------------------------------------------------
# check_health()
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_check_health_returns_ok_when_node_reports_ok(monkeypatch):
    def fake_urlopen(request, timeout):
        return _FakeHttpResponse(_rpc_ok("ok"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    health = await provider.check_health()

    assert health.status == HealthStatus.OK
    assert health.is_ok is True
    assert health.chain == Chain.SOLANA


@pytest.mark.asyncio
async def test_check_health_never_raises_on_rpc_error(monkeypatch):
    def fake_urlopen(request, timeout):
        return _FakeHttpResponse(_rpc_error(-32005, "Node is unhealthy"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    health = await provider.check_health()  # must not raise

    assert health.status == HealthStatus.ERROR
    assert health.is_ok is False
    assert "unhealthy" in health.message.lower()


@pytest.mark.asyncio
async def test_check_health_never_raises_on_connection_failure(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    # Avoid real sleeping during retries in this test.
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=2, backoff_base_seconds=0.01)
    health = await provider.check_health()  # must not raise

    assert health.status == HealthStatus.ERROR
    assert health.chain == Chain.SOLANA


async def _instant_sleep(_seconds):
    """A drop-in replacement for asyncio.sleep that doesn't actually wait,
    so retry tests run instantly instead of really backing off."""
    return None


# ----------------------------------------------------------------------
# Retries and backoff (PROJECT_SPEC.md section 32)
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retries_on_429_rate_limit_then_succeeds(monkeypatch):
    call_count = {"n": 0}

    def fake_urlopen(request, timeout):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise urllib.error.HTTPError(VALID_RPC_URL, 429, "Too Many Requests", {}, None)
        return _FakeHttpResponse(_rpc_ok("ok"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=5, backoff_base_seconds=0.01)
    health = await provider.check_health()

    assert health.status == HealthStatus.OK
    assert call_count["n"] == 3  # failed twice, succeeded on the third try


@pytest.mark.asyncio
async def test_retries_on_server_error_then_succeeds(monkeypatch):
    call_count = {"n": 0}

    def fake_urlopen(request, timeout):
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise urllib.error.HTTPError(VALID_RPC_URL, 503, "Service Unavailable", {}, None)
        return _FakeHttpResponse(_rpc_ok("ok"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=3, backoff_base_seconds=0.01)
    health = await provider.check_health()

    assert health.status == HealthStatus.OK
    assert call_count["n"] == 2


@pytest.mark.asyncio
async def test_gives_up_after_max_retries_and_reports_error_not_crash(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(VALID_RPC_URL, 503, "Service Unavailable", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=3, backoff_base_seconds=0.01)
    health = await provider.check_health()

    assert health.status == HealthStatus.ERROR
    assert "503" in health.message


@pytest.mark.asyncio
async def test_does_not_retry_on_non_retryable_client_error(monkeypatch):
    call_count = {"n": 0}

    def fake_urlopen(request, timeout):
        call_count["n"] += 1
        raise urllib.error.HTTPError(VALID_RPC_URL, 400, "Bad Request", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=5, backoff_base_seconds=0.01)
    health = await provider.check_health()

    assert health.status == HealthStatus.ERROR
    # A 400 (our request was bad) should fail immediately, not be retried
    # 5 times — retrying a malformed request will never succeed.
    assert call_count["n"] == 1


# ----------------------------------------------------------------------
# get_token_supply()
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_token_supply_returns_normalized_result(monkeypatch):
    # Response shape copied exactly from solana.com/docs/rpc/http/gettokensupply
    result = {
        "context": {"apiVersion": "3.1.8", "slot": 1114},
        "value": {"amount": "100000", "decimals": 2, "uiAmount": 1000, "uiAmountString": "1000"},
    }

    def fake_urlopen(request, timeout):
        return _FakeHttpResponse(_rpc_ok(result))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    supply = await provider.get_token_supply(TOKEN_ADDRESS)

    assert isinstance(supply, TokenSupply)
    assert supply.token_address == TOKEN_ADDRESS
    assert supply.amount == "100000"
    assert supply.decimals == 2
    assert supply.ui_amount == 1000


@pytest.mark.asyncio
async def test_get_token_supply_returns_none_for_invalid_address():
    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    result = await provider.get_token_supply("not-a-real-address")
    assert result is None


@pytest.mark.asyncio
async def test_get_token_supply_returns_none_not_fake_data_on_rpc_failure(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(VALID_RPC_URL, 400, "Bad Request", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=2, backoff_base_seconds=0.01)
    result = await provider.get_token_supply(TOKEN_ADDRESS)

    # Per AGENTS.md rule 6: never invent data. A failure must become None,
    # never a made-up TokenSupply.
    assert result is None


# ----------------------------------------------------------------------
# get_token_largest_accounts()
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_token_largest_accounts_returns_normalized_result(monkeypatch):
    # Response shape copied exactly from
    # solana.com/docs/rpc/http/gettokenlargestaccounts
    result = {
        "context": {"apiVersion": "3.1.8", "slot": 1114},
        "value": [
            {
                "address": "FYjHNoFtSQ5uijKrZFyYAxvEr87hsKXkXcxkcmkBAf4r",
                "amount": "771",
                "decimals": 2,
                "uiAmount": 7.71,
                "uiAmountString": "7.71",
            },
            {
                "address": "BnsywxTcaYeNUtzrPxQUvzAWxfzZe3ZLUJ4wMMuLESnu",
                "amount": "229",
                "decimals": 2,
                "uiAmount": 2.29,
                "uiAmountString": "2.29",
            },
        ],
    }

    def fake_urlopen(request, timeout):
        return _FakeHttpResponse(_rpc_ok(result))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    largest = await provider.get_token_largest_accounts(TOKEN_ADDRESS)

    assert isinstance(largest, TokenLargestAccounts)
    assert largest.token_address == TOKEN_ADDRESS
    assert len(largest.accounts) == 2
    assert largest.accounts[0].address == "FYjHNoFtSQ5uijKrZFyYAxvEr87hsKXkXcxkcmkBAf4r"
    assert largest.accounts[0].amount == "771"
    assert largest.accounts[0].ui_amount == 7.71


@pytest.mark.asyncio
async def test_get_token_largest_accounts_respects_limit(monkeypatch):
    result = {
        "context": {"slot": 1},
        "value": [
            {"address": f"addr{i}", "amount": "1", "decimals": 0, "uiAmount": 1}
            for i in range(5)
        ],
    }

    def fake_urlopen(request, timeout):
        return _FakeHttpResponse(_rpc_ok(result))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    largest = await provider.get_token_largest_accounts(TOKEN_ADDRESS, limit=2)

    assert len(largest.accounts) == 2


@pytest.mark.asyncio
async def test_get_token_largest_accounts_returns_none_for_invalid_address():
    provider = SolanaProvider(rpc_url=VALID_RPC_URL)
    result = await provider.get_token_largest_accounts("not-a-real-address")
    assert result is None


@pytest.mark.asyncio
async def test_get_token_largest_accounts_returns_none_on_persistent_failure(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("DNS failure")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("asyncio.sleep", _instant_sleep)

    provider = SolanaProvider(rpc_url=VALID_RPC_URL, max_retries=2, backoff_base_seconds=0.01)
    result = await provider.get_token_largest_accounts(TOKEN_ADDRESS)

    assert result is None


# ----------------------------------------------------------------------
# No trading / signing surface exists (AGENTS.md rules 4 and 5)
# ----------------------------------------------------------------------

def test_provider_has_no_trading_or_signing_methods():
    forbidden_substrings = ["sign", "buy", "sell", "swap", "trade", "transfer", "send"]
    method_names = [name for name in dir(SolanaProvider) if not name.startswith("_")]

    for name in method_names:
        lowered = name.lower()
        for forbidden in forbidden_substrings:
            assert forbidden not in lowered, (
                f"SolanaProvider has a method '{name}' that looks like it "
                f"could sign or trade — this must never exist (AGENTS.md rules 4/5)."
            )


def test_provider_never_accepts_a_private_key_or_seed_phrase_parameter():
    import inspect

    for name, method in inspect.getmembers(SolanaProvider, predicate=inspect.isfunction):
        params = inspect.signature(method).parameters
        for param_name in params:
            lowered = param_name.lower()
            assert "private" not in lowered
            assert "secret" not in lowered
            assert "seed" not in lowered
