#!/usr/bin/env python3

from hypothesis import given
from hypothesis import strategies as st

from ethereum_node.utils.rlp import decode, encode


def test_rlp_encode_bytes():
    assert encode(b"") == b"\x80"
    assert encode(b"\x01") == b"\x01"
    assert encode(b"\x7f") == b"\x7f"
    assert encode(b"\x80") == b"\x81\x80"
    assert encode(b"\x00" * 56) == b"\xb8\x38" + b"\x00" * 56


def test_rlp_encode_int():
    assert encode(0) == b"\x80"
    assert encode(15) == b"\x0f"
    assert encode(127) == b"\x7f"
    assert encode(128) == b"\x81\x80"
    assert encode(1024) == b"\x82\x04\x00"


def test_rlp_encode_list():
    assert encode([]) == b"\xc0"
    assert encode([b"\x01", b"\x02"]) == b"\xc2\x01\x02"
    assert encode([[], []]) == b"\xc2\xc0\xc0"
    assert encode([b"cat", [b"dog"]]) == b"\xc9\x83cat\xc4\x83dog"


def test_rlp_decode_bytes():
    assert decode(b"\x80") == b""
    assert decode(b"\x01") == b"\x01"
    assert decode(b"\x81\x80") == b"\x80"
    assert decode(b"\xb8\x38" + b"\x00" * 56) == b"\x00" * 56


def test_rlp_decode_int_encoding_roundtrip():
    for val in [0, 1, 15, 127, 128, 255, 256, 1024, 2**64 - 1]:
        rlp = encode(val)
        out = decode(rlp)
        assert isinstance(out, bytes)  # decode always returns bytes
        assert int.from_bytes(out, "big") == val


def test_rlp_decode_lists():
    assert decode(b"\xc2\x01\x02") == [b"\x01", b"\x02"]
    assert decode(b"\xc2\xc0\xc0") == [[], []]
    assert decode(b"\xc8\x83cat\xc4\x83dog") == [b"cat", [b"dog"]]


def test_rlp_encode_decode_roundtrip():
    cases = [
        b"",
        b"\x00",
        b"\x7f",
        b"\x80",
        b"hello",
        0,
        127,
        128,
        255,
        1024,
        [b"cat", b"dog"],
        [[b"\x00"], [b"\x01", b"\x02"]],
    ]
    for case in cases:
        roundtripped = decode(encode(case))
        assert roundtripped == case or (
            isinstance(case, int) and int.from_bytes(roundtripped, "big") == case
        )


@given(st.lists(st.binary(min_size=0, max_size=8), max_size=5))
def test_rlp_roundtrip_hypothesis(values):
    encoded = encode(values)
    decoded = decode(encoded)
    assert decoded == values
