"""Tests for app/models/wallet.py"""

import pytest

from app.models.chain import Chain
from app.models.wallet import WalletIdentity


def test_same_chain_and_address_are_equal():
    a = WalletIdentity(Chain.ETHEREUM, "0xABCDEF1234567890")
    b = WalletIdentity(Chain.ETHEREUM, "0xABCDEF1234567890")
    assert a == b
    assert hash(a) == hash(b)


def test_evm_wallet_addresses_are_case_insensitive_for_identity():
    a = WalletIdentity(Chain.BASE, "0xABCDEF")
    b = WalletIdentity(Chain.BASE, "0xabcdef")
    assert a == b


def test_solana_wallet_addresses_are_case_sensitive():
    a = WalletIdentity(Chain.SOLANA, "AbCdEf")
    b = WalletIdentity(Chain.SOLANA, "abcdef")
    assert a != b


def test_same_address_on_different_evm_chains_is_not_automatically_merged():
    # This is the specific warning in PROJECT_SPEC.md section 7: don't
    # assume the same address on two EVM chains is "the same" wallet.
    eth_wallet = WalletIdentity(Chain.ETHEREUM, "0xSAME")
    arbitrum_wallet = WalletIdentity(Chain.ARBITRUM, "0xSAME")

    assert eth_wallet != arbitrum_wallet
    assert eth_wallet.chain != arbitrum_wallet.chain


def test_empty_wallet_address_is_rejected():
    with pytest.raises(ValueError):
        WalletIdentity(Chain.SOLANA, "")


def test_wallet_identity_can_be_used_as_dict_key():
    identity = WalletIdentity(Chain.ETHEREUM, "0xABC")
    lookup = {identity: "wallet record"}
    assert lookup[WalletIdentity(Chain.ETHEREUM, "0XABC")] == "wallet record"


def test_wallet_identity_string_representation_includes_chain_and_address():
    identity = WalletIdentity(Chain.SOLANA, "ABC123")
    text = str(identity)
    assert "solana" in text
    assert "ABC123" in text
