#!/usr/bin/env python3

import pytest
from ethereum_node.evm.vm import EVM
from ethereum_node.evm.stack import EVMStack
from ethereum_node.evm.memory import Memory
from ethereum_node.evm.storage import JournaledStorage

class DummyTracer:
    def __init__(self):
        self.steps = []

    def step(self, vm, opcode):
        self.steps.append((vm.pc - 1, opcode))


def test_addition():
    # PUSH1 0x03 PUSH1 0x04 ADD STOP
    code = bytes([0x60, 0x03, 0x60, 0x04, 0x01, 0x00])
    evm = EVM(code)
    evm.run()
    assert evm.stack.pop() == 7


def test_memory_return():
    code = bytes([
        0x60, 0x00,  # PUSH1 0x00 (offset)
        0x60, 0x02,  # PUSH1 0x02 (size)
        0xf3         # RETURN
    ])
    evm = EVM(code)
    evm.memory.store(0, b"hi")
    result = evm.run()
    assert result == b"hi"


def test_out_of_gas():
    code = bytes([0x60, 0x02])  # PUSH1 0x02
    evm = EVM(code, gas=0)
    with pytest.raises(Exception, match="Out of gas"):
        evm.run()


def test_invalid_opcode():
    code = bytes([0xfe])
    evm = EVM(code)
    with pytest.raises(NotImplementedError):
        evm.run()


def test_tracer():
    code = bytes([0x60, 0x01, 0x60, 0x02, 0x01, 0x00])  # PUSH1 1, PUSH1 2, ADD, STOP
    tracer = DummyTracer()
    evm = EVM(code, tracer=tracer)
    evm.run()
    assert [op for _, op in tracer.steps] == [0x60, 0x60, 0x01, 0x00]
