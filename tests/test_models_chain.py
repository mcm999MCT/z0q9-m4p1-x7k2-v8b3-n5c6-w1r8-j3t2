"""Tests for app/models/chain.py"""

import pytest

from app.models.chain import (
    CHAIN_INFO,
    Chain,
    all_chains,
    chain_from_id,
    get_chain_info,
    is_evm_chain,
)


def test_all_six_expected_chains_exist():
    expected = {"solana", "ethereum", "base", "bnb", "arbitrum", "robinhood"}
    actual = {chain.value for chain in Chain}
    assert actual == expected


def test_all_chains_returns_all_six():
    chains = all_chains()
    assert len(chains) == 6
    assert len(set(chains)) == 6  # no duplicates


@pytest.mark.parametrize(
    "chain,expected_id",
    [
        (Chain.SOLANA, None),
        (Chain.ETHEREUM, 1),
        (Chain.BASE, 8453),
        (Chain.BNB, 56),
        (Chain.ARBITRUM, 42161),
        (Chain.ROBINHOOD, 4663),
    ],
)
def test_chain_ids_match_project_spec(chain, expected_id):
    # These exact numbers come from PROJECT_SPEC.md section 4.
    assert get_chain_info(chain).chain_id == expected_id


def test_solana_is_not_evm():
    assert is_evm_chain(Chain.SOLANA) is False


@pytest.mark.parametrize(
    "chain", [Chain.ETHEREUM, Chain.BASE, Chain.BNB, Chain.ARBITRUM, Chain.ROBINHOOD]
)
def test_evm_chains_are_flagged_as_evm(chain):
    assert is_evm_chain(chain) is True


def test_chain_from_id_finds_correct_chain():
    assert chain_from_id(1) == Chain.ETHEREUM
    assert chain_from_id(8453) == Chain.BASE
    assert chain_from_id(56) == Chain.BNB
    assert chain_from_id(42161) == Chain.ARBITRUM
    assert chain_from_id(4663) == Chain.ROBINHOOD


def test_chain_from_id_returns_none_for_unknown_id():
    assert chain_from_id(999999) is None


def test_every_chain_has_a_display_name():
    for chain in Chain:
        info = get_chain_info(chain)
        assert info.display_name
        assert isinstance(info.display_name, str)


def test_chain_info_registry_covers_every_chain_enum_value():
    assert set(CHAIN_INFO.keys()) == set(Chain)
