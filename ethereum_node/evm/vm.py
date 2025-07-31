#!/usr/bin/env python3

from ethereum_node.evm.stack import EVMStack
from ethereum_node.evm.memory import Memory
from ethereum_node.evm.storage import JournaledStorage
from ethereum_node.evm.opcodes import OPCODES
from ethereum_node.evm.opcodes import Halt
from ethereum_node.evm.gas import GAS_COSTS

class EVM:
    def __init__(self, code, gas=10**6, tracer=None):
        self.code = code                  # bytecode to execute
        self.pc = 0                       # program counter
        self.stack = EVMStack()
        self.memory = Memory()
        self.storage = JournaledStorage()
        self.gas_left = gas
        self.tracer = tracer              # optional hook: tracer.step(vm)

    def read_bytes(self, n):
        data = self.code[self.pc : self.pc + n]
        self.pc += n
        return data

    def step(self):
        if self.pc >= len(self.code):
            raise Halt()

        opcode = self.code[self.pc]
        self.pc += 1

        if self.tracer:
            self.tracer.step(self, opcode)

        self.gas_left -= GAS_COSTS.get(opcode, 0)
        if self.gas_left < 0:
            raise Exception("Out of gas")

        if opcode not in OPCODES:
            raise NotImplementedError(f"Opcode {hex(opcode)} not supported")

        handler = OPCODES[opcode]
        handler(self)

    def run(self):
        try:
            while True:
                self.step()
        except Halt as h:
            return h.return_data
