#!/usr/bin/env python3

# evm/stack.py

STACK_LIMIT = 1024

class StackOverflow(Exception):
    pass

class StackUnderflow(Exception):
    pass

class EVMStack:
    def __init__(self):
        self._data = []

    def push(self, value: int):
        if not (0 <= value < 2**256):
            raise ValueError("Stack value must be a 256-bit integer")
        if len(self._data) >= STACK_LIMIT:
            raise StackOverflow("Stack overflow")
        self._data.append(value)

    def pop(self, index: int = 0) -> int:
        """Pop from top with optional depth index (0 = top)"""
        if index >= len(self._data):
            raise StackUnderflow("Pop index out of bounds")
        return self._data.pop(-1 - index)

    def peek(self, index: int = 0) -> int:
        """Peek from the top, 0-based (0 = top item, 1 = next)"""
        if index >= len(self._data):
            raise StackUnderflow("Peek index out of bounds")
        return self._data[-1 - index]

    def set(self, index: int, value: int):
        """Set value at depth index (0 = top item)"""
        if not (0 <= value < 2**256):
            raise ValueError("Value must be 256-bit")
        if index >= len(self._data):
            raise StackUnderflow("Set index out of bounds")
        self._data[-1 - index] = value

    def __len__(self):
        return len(self._data)
