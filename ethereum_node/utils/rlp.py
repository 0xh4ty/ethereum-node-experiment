from typing import List, Tuple, Union

RLP = Union[bytes, int, List["RLP"]]  # Recursive type


def encode(item: RLP) -> bytes:
    if isinstance(item, int):
        if item == 0:
            return b"\x80"
        elif item < 128:
            return bytes([item])
        else:
            b = item.to_bytes((item.bit_length() + 7) // 8, "big")
            return _encode_bytes(b)
    elif isinstance(item, bytes):
        return _encode_bytes(item)
    elif isinstance(item, list):
        encoded_elements = b"".join(encode(i) for i in item)
        return _encode_length(len(encoded_elements), 0xC0) + encoded_elements
    else:
        raise TypeError(f"Unsupported RLP type: {type(item)}")


def decode(encoded: bytes) -> RLP:
    item, _ = _decode_item(encoded, 0)
    return item


# --- Internal helpers ---


def _encode_bytes(b: bytes) -> bytes:
    if len(b) == 1 and b[0] < 128:
        return b
    else:
        return _encode_length(len(b), 0x80) + b


def _encode_length(length: int, offset: int) -> bytes:
    if length < 56:
        return bytes([offset + length])
    else:
        length_bytes = length.to_bytes((length.bit_length() + 7) // 8, "big")
        return bytes([offset + 55 + len(length_bytes)]) + length_bytes


def _decode_item(data: bytes, pos: int) -> Tuple[RLP, int]:
    if pos >= len(data):
        raise ValueError("Unexpected end of RLP data")

    prefix = data[pos]
    if prefix <= 0x7F:
        return data[pos : pos + 1], pos + 1
    elif prefix <= 0xB7:
        length = prefix - 0x80
        if length == 0:
            return b"", pos + 1
        return data[pos + 1 : pos + 1 + length], pos + 1 + length
    elif prefix <= 0xBF:
        lenlen = prefix - 0xB7
        length = int.from_bytes(data[pos + 1 : pos + 1 + lenlen], "big")
        start = pos + 1 + lenlen
        return data[start : start + length], start + length
    elif prefix <= 0xF7:
        length = prefix - 0xC0
        out = []
        i = pos + 1
        end = i + length
        while i < end:
            item, i = _decode_item(data, i)
            out.append(item)
        return out, i
    else:
        lenlen = prefix - 0xF7
        length = int.from_bytes(data[pos + 1 : pos + 1 + lenlen], "big")
        start = pos + 1 + lenlen
        out = []
        i = start
        end = start + length
        while i < end:
            item, i = _decode_item(data, i)
            out.append(item)
        return out, i
