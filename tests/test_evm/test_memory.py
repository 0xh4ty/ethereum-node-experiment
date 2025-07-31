#!/usr/bin/env python3

import pytest
from ethereum_node.evm.memory import Memory

def test_memory_store_and_load():
    mem = Memory()
    mem.store(0, b"abc")
    assert mem.load(0, 3) == b"abc"
    assert mem.load(0, 5) == b"abc\x00\x00"  # padded read
    assert mem.load(1, 2) == b"bc"

def test_memory_extend():
    mem = Memory()
    mem.store(35, b"xyz")
    assert len(mem) % 32 == 0
    assert len(mem) >= 38  # 35 + 3
    assert mem.load(35, 3) == b"xyz"
    assert mem.load(0, 35) == b"\x00" * 35  # prior uninitialized bytes

def test_memory_load_beyond_written_region():
    mem = Memory()
    mem.store(0, b"data")
    assert mem.load(0, 10) == b"data" + b"\x00" * 6

def test_memory_store_negative_offset():
    mem = Memory()
    with pytest.raises(ValueError):
        mem.store(-1, b"\x00")

def test_memory_load_negative_args():
    mem = Memory()
    with pytest.raises(ValueError):
        mem.load(-1, 10)
    with pytest.raises(ValueError):
        mem.load(0, -5)
