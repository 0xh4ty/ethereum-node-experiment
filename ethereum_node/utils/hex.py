from typing import Optional


def hex_to_bytes(s: str) -> bytes:
    """Convert hex string (with or without 0x) to bytes."""
    s = s.lower()
    if s.startswith("0x"):
        s = s[2:]
    if len(s) % 2 != 0:
        s = "0" + s
    return bytes.fromhex(s)


def bytes_to_hex(b: bytes, with_prefix: bool = True) -> str:
    """Convert bytes to hex string with optional 0x prefix."""
    hex_str = b.hex()
    return "0x" + hex_str if with_prefix else hex_str


def int_to_bytes(value: int, length: int = None) -> bytes:
    """Convert int to minimal bytes (or fixed length if given)."""
    if value < 0:
        raise ValueError("int must be non-negative")
    byte_len = (value.bit_length() + 7) // 8 or 1
    result = value.to_bytes(byte_len, byteorder="big")
    if length is not None:
        result = result.rjust(length, b"\x00")
    return result


def bytes_to_int(b: bytes) -> int:
    """Convert bytes to int."""
    return int.from_bytes(b, byteorder="big")


def pad_left(b: bytes, length: int) -> bytes:
    """Pad bytes to the left with zeros."""
    return b.rjust(length, b"\x00")


def pad_right(b: bytes, length: int) -> bytes:
    """Pad bytes to the right with zeros."""
    return b.ljust(length, b"\x00")
