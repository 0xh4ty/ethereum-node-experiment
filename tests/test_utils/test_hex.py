#!/usr/bin/env python3

from ethereum_node.utils.hex import (bytes_to_hex, bytes_to_int, hex_to_bytes,
                                     int_to_bytes, pad_left, pad_right)


def test_hex_to_bytes():
    assert hex_to_bytes("0x00") == b"\x00"
    assert hex_to_bytes("ff") == b"\xff"
    assert hex_to_bytes("0abc") == b"\x0a\xbc"
    assert hex_to_bytes("abc") == b"\x0a\xbc"  # odd-length padding


def test_bytes_to_hex():
    assert bytes_to_hex(b"\x00") == "0x00"
    assert bytes_to_hex(b"\xff", with_prefix=False) == "ff"
    assert bytes_to_hex(b"\xde\xad\xbe\xef") == "0xdeadbeef"


def test_int_to_bytes():
    assert int_to_bytes(0) == b"\x00"
    assert int_to_bytes(255) == b"\xff"
    assert int_to_bytes(256) == b"\x01\x00"
    assert int_to_bytes(1, length=4) == b"\x00\x00\x00\x01"


def test_bytes_to_int():
    assert bytes_to_int(b"\x00") == 0
    assert bytes_to_int(b"\xff") == 255
    assert bytes_to_int(b"\x01\x00") == 256


def test_pad_left():
    assert pad_left(b"\x01", 4) == b"\x00\x00\x00\x01"
    assert pad_left(b"", 2) == b"\x00\x00"


def test_pad_right():
    assert pad_right(b"\x01", 4) == b"\x01\x00\x00\x00"
    assert pad_right(b"", 3) == b"\x00\x00\x00"
