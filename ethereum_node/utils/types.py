from typing import NewType

Address = NewType("Address", bytes)  # Must be 20 bytes
Hash = NewType("Hash", bytes)  # Must be 32 bytes
U256 = NewType("U256", int)  # Int in [0, 2**256)


def is_valid_address(addr: bytes) -> bool:
    return isinstance(addr, bytes) and len(addr) == 20


def is_valid_hash(h: bytes) -> bool:
    return isinstance(h, bytes) and len(h) == 32


def to_address(data: bytes) -> Address:
    if not is_valid_address(data):
        raise ValueError("Address must be 20 bytes")
    return Address(data)


def to_hash(data: bytes) -> Hash:
    if not is_valid_hash(data):
        raise ValueError("Hash must be 32 bytes")
    return Hash(data)


def to_u256(x: int) -> U256:
    if not isinstance(x, int) or x < 0 or x >= 2**256:
        raise ValueError("U256 must be in range [0, 2**256)")
    return U256(x)
