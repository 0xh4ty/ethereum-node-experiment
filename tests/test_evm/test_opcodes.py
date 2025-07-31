#!/usr/bin/env python3

import hashlib
import pytest
from ethereum_node.evm.stack import EVMStack
from ethereum_node.evm.memory import Memory
from ethereum_node.evm.storage import JournaledStorage
from ethereum_node.evm.opcodes import OPCODES
from ethereum_node.evm.opcodes import Halt

class DummyContext:
    def __init__(self):
        self.stack = EVMStack()
        self.memory = Memory()
        self.storage = JournaledStorage()
        self.pc = 0
        self.code = b""
        self.return_data = b""
        self.stopped = False
        self.gas_left = 10**6

    def read_bytes(self, n):
        data = self.code[self.pc + 1 : self.pc + 1 + n]
        self.pc += n
        return data


def run_opcode(opcode: int, ctx: DummyContext):
    handler = OPCODES[opcode]
    handler(ctx)

# --- Tests for individual opcodes ---

def test_push1():
    ctx = DummyContext()
    ctx.code = bytes([0x60, 0x2a])  # PUSH1 0x2a
    ctx.pc = 0
    run_opcode(0x60, ctx)
    assert ctx.stack.pop() == 0x2a

def test_pop():
    ctx = DummyContext()
    ctx.stack.push(0xdead)
    run_opcode(0x50, ctx)  # POP
    with pytest.raises(Exception):
        ctx.stack.pop()

def test_dup():
    ctx = DummyContext()
    ctx.stack.push(0x12)
    run_opcode(0x80, ctx)  # DUP1
    assert ctx.stack.pop() == 0x12
    assert ctx.stack.pop() == 0x12

def test_swap():
    ctx = DummyContext()
    ctx.stack.push(0x01)
    ctx.stack.push(0x02)
    run_opcode(0x90, ctx)  # SWAP1
    assert ctx.stack.pop() == 0x01
    assert ctx.stack.pop() == 0x02

@pytest.mark.parametrize("opcode,a,b,expected", [
    (0x01, 2, 3, 5),     # ADD
    (0x02, 2, 4, 8),     # MUL
    (0x03, 5, 3, 2),     # SUB
    (0x04, 8, 2, 4),     # DIV
    (0x06, 9, 4, 1),     # MOD
])
def test_basic_arithmetic(opcode, a, b, expected):
    ctx = DummyContext()
    ctx.stack.push(a)
    ctx.stack.push(b)
    run_opcode(opcode, ctx)
    assert ctx.stack.pop() == expected

def test_stop():
    ctx = DummyContext()
    with pytest.raises(Halt):
        run_opcode(0x00, ctx)

def test_return():
    ctx = DummyContext()
    ctx.memory.store(0, b"hello world")
    ctx.stack.push(0)           # offset
    ctx.stack.push(11)          # size

    with pytest.raises(Halt) as exc_info:
        run_opcode(0xf3, ctx)   # RETURN

    assert exc_info.value.return_data == b"hello world"

# --- SHA3 ---

def test_sha3():
    ctx = DummyContext()
    ctx.memory.store(0, b"abc")
    ctx.stack.push(3)   # size
    ctx.stack.push(0)   # offset
    run_opcode(0x20, ctx)  # SHA3
    hashed = ctx.stack.pop()

    from ethereum_node.utils.hash import keccak256
    expected = int.from_bytes(keccak256(b"abc"), "big")
    assert hashed == expected

# --- Memory Load/Store already implicitly tested in test_return ---
# Optional explicit test if desired:

def test_memory_store_and_load():
    m = Memory()
    m.store(10, b"\x12\x34\x56")
    result = m.load(10, 3)
    assert result == b"\x12\x34\x56"

# --- Storage ---

def test_sstore_and_sload():
    ctx = DummyContext()
    key = 0xabc
    value = 0xdeadbeef
    ctx.stack.push(key)
    ctx.stack.push(value)
    run_opcode(0x55, ctx)  # SSTORE

    ctx.stack.push(key)
    run_opcode(0x54, ctx)  # SLOAD
    assert ctx.stack.pop() == value

# --- Control Flow Tests ---

def test_jump_valid():
    ctx = DummyContext()
    ctx.code = b"\x00" * 10 + b"\x5b"  # JUMPDEST at position 10
    ctx.stack.push(10)
    run_opcode(0x56, ctx)  # JUMP
    assert ctx.pc == 9

def test_jump_invalid():
    ctx = DummyContext()
    ctx.code = b"\x00" * 10
    ctx.stack.push(5)
    with pytest.raises(Exception):
        run_opcode(0x56, ctx)

def test_jumpi_taken():
    ctx = DummyContext()
    ctx.code = b"\x00" * 20 + b"\x5b"
    ctx.stack.push(1)   # condition true
    ctx.stack.push(20)  # destination
    run_opcode(0x57, ctx)
    assert ctx.pc == 19

def test_jumpi_not_taken():
    ctx = DummyContext()
    ctx.pc = 5
    ctx.stack.push(0)   # condition false
    ctx.stack.push(20)  # destination
    run_opcode(0x57, ctx)
    assert ctx.pc == 5  # no jump

def test_jumpdest():
    ctx = DummyContext()
    run_opcode(0x5b, ctx)  # no-op

# --- Call-like Stubs ---

def test_call_stub():
    ctx = DummyContext()
    for _ in range(7):
        ctx.stack.push(0)
    run_opcode(0xf1, ctx)  # CALL
    assert ctx.stack.pop() == 1

def test_delegatecall_stub():
    ctx = DummyContext()
    for _ in range(6):
        ctx.stack.push(0)
    run_opcode(0xf4, ctx)  # DELEGATECALL
    assert ctx.stack.pop() == 1

# --- Create / Terminate ---

def test_create_stub():
    ctx = DummyContext()
    for _ in range(3):
        ctx.stack.push(0)
    run_opcode(0xf0, ctx)
    assert ctx.stack.pop() == 0xdeadbeef

def test_create2_stub():
    ctx = DummyContext()
    for _ in range(4):
        ctx.stack.push(0)
    run_opcode(0xf5, ctx)
    assert ctx.stack.pop() == 0xbeefdead

def test_selfdestruct():
    ctx = DummyContext()
    ctx.stack.push(0)
    with pytest.raises(Halt):
        run_opcode(0xff, ctx)

def test_revert():
    ctx = DummyContext()
    ctx.memory.store(0, b"oops!")
    ctx.stack.push(5)  # size
    ctx.stack.push(0)  # offset
    with pytest.raises(Halt) as exc_info:
        run_opcode(0xfd, ctx)
    assert exc_info.value.return_data == b"oops!"
