"""Tests for app/models/token.py"""

import pytest

from app.models.chain import Chain
from app.models.token import Token, TokenIdentity, normalize_address


def test_same_chain_and_address_are_equal():
    a = TokenIdentity(Chain.ETHEREUM, "0xABCDEF1234567890")
    b = TokenIdentity(Chain.ETHEREUM, "0xABCDEF1234567890")
    assert a == b
    assert hash(a) == hash(b)


def test_evm_addresses_are_case_insensitive_for_identity():
    a = TokenIdentity(Chain.ETHEREUM, "0xABCDEF1234567890")
    b = TokenIdentity(Chain.ETHEREUM, "0xabcdef1234567890")
    assert a == b


def test_solana_addresses_are_case_sensitive():
    # Solana uses base58 encoding, where case matters.
    a = TokenIdentity(Chain.SOLANA, "AbCdEf123")
    b = TokenIdentity(Chain.SOLANA, "abcdef123")
    assert a != b


def test_same_address_on_different_chains_is_not_equal():
    # This is the core rule from PROJECT_SPEC.md section 6: address alone
    # is never a sufficient identifier.
    eth_token = TokenIdentity(Chain.ETHEREUM, "0xABC123")
    base_token = TokenIdentity(Chain.BASE, "0xABC123")
    robinhood_token = TokenIdentity(Chain.ROBINHOOD, "0xABC123")

    assert eth_token != base_token
    assert eth_token != robinhood_token
    assert base_token != robinhood_token


def test_whitespace_is_trimmed():
    a = TokenIdentity(Chain.SOLANA, "  ABC123  ")
    b = TokenIdentity(Chain.SOLANA, "ABC123")
    assert a == b


def test_empty_address_is_rejected():
    with pytest.raises(ValueError):
        TokenIdentity(Chain.SOLANA, "")

    with pytest.raises(ValueError):
        TokenIdentity(Chain.SOLANA, "   ")


def test_token_identity_can_be_used_as_dict_key():
    identity = TokenIdentity(Chain.ETHEREUM, "0xABC123")
    lookup = {identity: "some value"}
    assert lookup[TokenIdentity(Chain.ETHEREUM, "0XABC123")] == "some value"


def test_token_wraps_identity_and_exposes_convenience_properties():
    identity = TokenIdentity(Chain.SOLANA, "ABC123")
    token = Token(identity=identity, symbol="ABC", name="Example Token")

    assert token.chain == Chain.SOLANA
    assert token.token_address == "ABC123"
    assert token.symbol == "ABC"
    assert token.name == "Example Token"


def test_token_symbol_and_name_default_to_none_not_fake_values():
    identity = TokenIdentity(Chain.SOLANA, "ABC123")
    token = Token(identity=identity)

    # Per AGENTS.md rule 6: unknown data must be None/"UNKNOWN", never a
    # made-up value.
    assert token.symbol is None
    assert token.name is None


def test_normalize_address_lowercases_only_for_evm():
    assert normalize_address(Chain.ETHEREUM, "0xABC") == "0xabc"
    assert normalize_address(Chain.SOLANA, "ABC") == "ABC"
