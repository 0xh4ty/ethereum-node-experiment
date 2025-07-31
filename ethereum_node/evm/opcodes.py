#!/usr/bin/env python3

from ethereum_node.evm.stack import EVMStack
from ethereum_node.evm.memory import Memory
from ethereum_node.evm.storage import JournaledStorage
from ethereum_node.evm.gas import GAS_COSTS
import operator
from ethereum_node.utils.hash import keccak256

class Halt(Exception):
    def __init__(self, return_data=b""):
        self.return_data = return_data


def stop(vm):
    raise Halt()


def op_push(vm, value: bytes):
    int_val = int.from_bytes(value, 'big')
    vm.stack.push(int_val)

def op_pop(vm):
    vm.stack.pop()


def make_dup(n):
    def dup(vm):
        vm.stack.push(vm.stack.peek(n - 1))
    return dup


def make_swap(n):
    def swap(vm):
        a = vm.stack.peek(0)
        b = vm.stack.peek(n)
        vm.stack.set(0, b)
        vm.stack.set(n, a)
    return swap


def op_return(vm):
    size = vm.stack.pop()
    offset = vm.stack.pop()
    data = vm.memory.load(offset, size)
    raise Halt(return_data=data)


def make_binop(fn):
    def binop(vm):
        b = vm.stack.pop()
        a = vm.stack.pop()
        vm.stack.push(fn(a, b) % 2**256)
    return binop


def evm_div(a: int, b: int) -> int:
    return 0 if b == 0 else a // b


def evm_sdiv(a: int, b: int) -> int:
    if b == 0:
        return 0
    # Convert to signed 256-bit integers
    a_signed = (a if a < 2**255 else a - 2**256)
    b_signed = (b if b < 2**255 else b - 2**256)
    result = abs(a_signed) // abs(b_signed)
    if (a_signed < 0) != (b_signed < 0):
        result = -result
    return result % 2**256  # Wrap back to uint256


# Mapping of opcode byte to handler function
OPCODES = {
    0x00: stop,
    0x01: make_binop(operator.add),
    0x02: make_binop(operator.mul),
    0x03: make_binop(operator.sub),
    0x04: make_binop(evm_div),
    0x05: make_binop(evm_sdiv),
    0x06: make_binop(operator.mod),
    0x50: op_pop,
    0xf3: op_return,
}

# PUSH1 to PUSH32
def make_push_n(n):
    def push_fn(vm):
        value = vm.read_bytes(n)
        op_push(vm, value)
    return push_fn

for i in range(1, 33):
    OPCODES[0x5f + i] = make_push_n(i)


# DUP1 to DUP16
for i in range(1, 17):
    OPCODES[0x7f + i] = make_dup(i)

# SWAP1 to SWAP16
for i in range(1, 17):
    OPCODES[0x8f + i] = make_swap(i)


def execute_opcode(vm, opcode):
    if opcode in OPCODES:
        OPCODES[opcode](vm)
    else:
        raise NotImplementedError(f"Opcode {hex(opcode)} not implemented")


# --- Memory operations ---
def mload(vm):
    offset = vm.stack.pop()
    data = vm.memory.load(offset, 32)
    vm.stack.push(int.from_bytes(data, 'big'))

def mstore(vm):
    offset = vm.stack.pop()
    value = vm.stack.pop()
    data = value.to_bytes(32, 'big')
    vm.memory.store(offset, data)

def mstore8(vm):
    offset = vm.stack.pop()
    value = vm.stack.pop() & 0xff
    vm.memory.store(offset, bytes([value]))

# --- SHA3 ---
def sha3(vm):
    offset = vm.stack.pop()
    size = vm.stack.pop()
    data = vm.memory.load(offset, size)
    hashed = keccak256(data)  # Simulate KECCAK256 with SHA3-256 placeholder
    vm.stack.push(int.from_bytes(hashed, 'big'))

# --- Storage operations ---
def sload(vm):
    key = vm.stack.pop()
    value = vm.storage.load(key)
    vm.stack.push(value)

def sstore(vm):
    value = vm.stack.pop()
    key = vm.stack.pop()
    vm.storage.store(key, value)

# --- Log operations ---
def make_log(n):
    def log_op(vm):
        offset = vm.stack.pop()
        size = vm.stack.pop()
        data = vm.memory.load(offset, size)
        topics = [vm.stack.pop() for _ in range(n)]
        # For now, we just print. Real EVM clients would emit a log event.
        print(f"LOG{n}: topics={topics}, data={data.hex()}")
    return log_op

# Register opcodes
OPCODES[0x20] = sha3
OPCODES[0x51] = mload
OPCODES[0x52] = mstore
OPCODES[0x53] = mstore8
OPCODES[0x54] = sload
OPCODES[0x55] = sstore

for i in range(5):
    OPCODES[0xa0 + i] = make_log(i)

# Control Flow
def is_valid_jumpdest(code: bytes, dest: int) -> bool:
    if dest >= len(code):
        return False
    return code[dest] == 0x5b  # 0x5b = JUMPDEST

def op_jump(vm):
    dest = vm.stack.pop()
    if not is_valid_jumpdest(vm.code, dest):
        raise Exception(f"Invalid jump destination: {hex(dest)}")
    vm.pc = dest - 1  # -1 because pc will be incremented after this

def op_jumpi(vm):
    dest = vm.stack.pop()
    cond = vm.stack.pop()
    if cond != 0:
        if not is_valid_jumpdest(vm.code, dest):
            raise Exception(f"Invalid jump destination: {hex(dest)}")
        vm.pc = dest - 1

def op_jumpdest(vm):
    pass  # Marker, does nothing

# Call-related Stubs
def call_stub(vm):
    # Pop the 7 arguments
    for _ in range(7):
        vm.stack.pop()
    vm.stack.push(1)  # Succeed by default (mock)

def delegatecall_stub(vm):
    for _ in range(6):
        vm.stack.pop()
    vm.stack.push(1)  # Succeed

# Create / Revert / Destruct
def op_create(vm):
    for _ in range(3):
        vm.stack.pop()
    vm.stack.push(0xdeadbeef)  # Dummy new address

def op_create2(vm):
    for _ in range(4):
        vm.stack.pop()
    vm.stack.push(0xbeefdead)

def op_selfdestruct(vm):
    vm.stack.pop()
    raise Halt()  # Ends execution, clears storage in real EVM

def op_revert(vm):
    offset = vm.stack.pop()
    size = vm.stack.pop()
    data = vm.memory.load(offset, size)
    raise Halt(return_data=data)  # Revert still returns data

# Control flow
OPCODES[0x56] = op_jump
OPCODES[0x57] = op_jumpi
OPCODES[0x5b] = op_jumpdest

# Call variants
OPCODES[0xf1] = call_stub           # CALL
OPCODES[0xf2] = call_stub           # CALLCODE
OPCODES[0xf4] = delegatecall_stub   # DELEGATECALL
OPCODES[0xfa] = delegatecall_stub   # STATICCALL

# Object creation / termination
OPCODES[0xf0] = op_create
OPCODES[0xf5] = op_create2
OPCODES[0xff] = op_selfdestruct
OPCODES[0xfd] = op_revert
