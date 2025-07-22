import pytest

from ethereum_node.utils.types import to_address, to_hash, to_u256


def test_address_valid():
    assert to_address(b"\x00" * 20) == b"\x00" * 20


def test_address_invalid():
    with pytest.raises(ValueError, match="Address must be 20 bytes"):
        to_address(b"\x00" * 19)


def test_hash_valid():
    assert to_hash(b"\xff" * 32) == b"\xff" * 32


def test_hash_invalid():
    with pytest.raises(ValueError, match="Hash must be 32 bytes"):
        to_hash(b"\xff" * 31)


def test_u256_valid():
    val = to_u256(0)
    assert isinstance(val, int)
    assert val == 0

    val = to_u256(2**255)
    assert isinstance(val, int)
    assert val == 2**255

    val = to_u256(2**256 - 1)
    assert isinstance(val, int)
    assert val == 2**256 - 1


def test_u256_invalid():
    with pytest.raises(ValueError, match="U256 must be in range"):
        to_u256(-1)

    with pytest.raises(ValueError, match="U256 must be in range"):
        to_u256(2**256)
