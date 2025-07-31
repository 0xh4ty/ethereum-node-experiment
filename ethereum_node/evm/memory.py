#!/usr/bin/env python3

WORD_SIZE = 32  # 32 bytes per word


class Memory:
    def __init__(self):
        self.data = bytearray()

    def extend(self, end: int):
        """Expand memory to cover [0:end), rounded up to nearest word."""
        if end <= len(self.data):
            return
        new_size = ((end + WORD_SIZE - 1) // WORD_SIZE) * WORD_SIZE
        self.data.extend(b"\x00" * (new_size - len(self.data)))

    def store(self, offset: int, value: bytes):
        """Write value at given offset."""
        if offset < 0:
            raise ValueError("Negative offset not allowed")
        end = offset + len(value)
        self.extend(end)
        self.data[offset:end] = value

    def load(self, offset: int, size: int) -> bytes:
        """Read `size` bytes starting at `offset`."""
        if offset < 0 or size < 0:
            raise ValueError("Offset and size must be non-negative")
        end = offset + size
        self.extend(end)
        return bytes(self.data[offset:end])

    def __len__(self):
        return len(self.data)
