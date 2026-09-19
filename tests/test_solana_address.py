"""Tests for app/chains/solana_address.py

Uses a couple of well-known, real Solana addresses purely to test address
FORMAT validation (base58, 32 bytes). No RPC calls are made — these are
just strings being checked for shape, not live blockchain data.
"""

import pytest

from app.chains.solana_address import is_valid_solana_address


# Wrapped SOL mint address — one of the most well-known Solana addresses.
WRAPPED_SOL_MINT = "So11111111111111111111111111111111111111112"

# USDC mint address on Solana mainnet — another widely known, real address.
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


def test_well_known_real_addresses_are_valid():
    assert is_valid_solana_address(WRAPPED_SOL_MINT) is True
    assert is_valid_solana_address(USDC_MINT) is True


def test_empty_string_is_invalid():
    assert is_valid_solana_address("") is False


def test_too_short_is_invalid():
    assert is_valid_solana_address("abc123") is False


def test_too_long_is_invalid():
    assert is_valid_solana_address("A" * 100) is False


def test_invalid_base58_characters_are_rejected():
    # '0' (zero), 'O', 'I', and 'l' are NOT in the base58 alphabet.
    invalid_with_zero = "0" + USDC_MINT[1:]
    assert is_valid_solana_address(invalid_with_zero) is False


def test_non_string_input_is_invalid():
    assert is_valid_solana_address(None) is False  # type: ignore[arg-type]
    assert is_valid_solana_address(12345) is False  # type: ignore[arg-type]


def test_whitespace_is_trimmed_before_checking():
    assert is_valid_solana_address(f"  {USDC_MINT}  ") is True


def test_random_valid_looking_but_wrong_length_base58_is_invalid():
    # Valid base58 characters, but doesn't decode to exactly 32 bytes.
    assert is_valid_solana_address("abcdefgh") is False


@pytest.mark.parametrize("bad_value", ["", "   ", "not-base58-!!!", "111"])
def test_various_malformed_inputs_never_raise(bad_value):
    # The function must never raise, only return True/False.
    assert is_valid_solana_address(bad_value) in (True, False)
