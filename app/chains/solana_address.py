"""
Solana address validation for the Crypto Intelligence Bot.

Solana addresses (both token mints and wallets) are 32-byte public keys
encoded using base58. Unlike Bitcoin addresses, they do NOT include a
checksum — validity means "is this valid base58 text that decodes to
exactly 32 bytes", nothing more. This module implements that check using
only Python's standard library, so no extra dependency is needed just to
validate an address shape.

This is intentionally a FORMAT check only. It does not (and cannot) tell
you whether an address actually exists on-chain — only a real RPC call
can tell you that.
"""

from __future__ import annotations

# The base58 alphabet Bitcoin/Solana use. Notably excludes 0 (zero), O
# (capital o), I (capital i), and l (lowercase L) to avoid visual
# ambiguity.
_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE58_INDEX = {char: index for index, char in enumerate(_BASE58_ALPHABET)}

# Solana public keys are exactly 32 bytes. Base58-encoded, that's roughly
# 32-44 characters depending on how many leading zero bytes there are.
_MIN_ADDRESS_LENGTH = 32
_MAX_ADDRESS_LENGTH = 44
_EXPECTED_DECODED_BYTES = 32


def _base58_decode(text: str) -> bytes:
    """Decode a base58 string into raw bytes.

    Raises ValueError if the string contains characters outside the
    base58 alphabet.
    """
    value = 0
    for char in text:
        try:
            digit = _BASE58_INDEX[char]
        except KeyError as exc:
            raise ValueError(f"Character {char!r} is not valid base58.") from exc
        value = value * 58 + digit

    # Convert the big integer to bytes.
    body = value.to_bytes((value.bit_length() + 7) // 8, "big") if value > 0 else b""

    # Each leading '1' character in base58 represents a leading zero byte.
    leading_zero_count = len(text) - len(text.lstrip("1"))
    return b"\x00" * leading_zero_count + body


def is_valid_solana_address(address: str) -> bool:
    """Check whether a string is plausibly a valid Solana address (public
    key), by format only.

    Returns False (never raises) for anything malformed, so callers can
    safely use this as a guard before making an RPC call.
    """
    if not isinstance(address, str):
        return False

    candidate = address.strip()
    if not (_MIN_ADDRESS_LENGTH <= len(candidate) <= _MAX_ADDRESS_LENGTH):
        return False

    try:
        decoded = _base58_decode(candidate)
    except ValueError:
        return False

    return len(decoded) == _EXPECTED_DECODED_BYTES
