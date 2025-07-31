#!/usr/bin/env python3

import pytest
from ethereum_node.evm.stack import EVMStack, StackOverflow, StackUnderflow

def test_push_pop_roundtrip():
    stack = EVMStack()
    stack.push(42)
    assert stack.pop() == 42

def test_push_invalid_value():
    stack = EVMStack()
    with pytest.raises(ValueError):
        stack.push(-1)
    with pytest.raises(ValueError):
        stack.push(2**256)

def test_pop_empty_stack():
    stack = EVMStack()
    with pytest.raises(StackUnderflow):
        stack.pop()

def test_peek_top():
    stack = EVMStack()
    stack.push(1)
    stack.push(2)
    assert stack.peek() == 2
    assert stack.peek(1) == 1

def test_peek_out_of_bounds():
    stack = EVMStack()
    stack.push(1)
    with pytest.raises(StackUnderflow):
        stack.peek(1)

def test_set_value():
    stack = EVMStack()
    stack.push(10)
    stack.push(20)
    stack.set(0, 30)
    assert stack.peek() == 30
    stack.set(1, 40)
    assert stack.peek(1) == 40

def test_set_invalid_value():
    stack = EVMStack()
    stack.push(1)
    with pytest.raises(ValueError):
        stack.set(0, -1)

def test_set_out_of_bounds():
    stack = EVMStack()
    stack.push(1)
    with pytest.raises(StackUnderflow):
        stack.set(1, 2)

def test_stack_overflow():
    stack = EVMStack()
    for i in range(1024):
        stack.push(i)
    with pytest.raises(StackOverflow):
        stack.push(999)

def test_stack_length():
    stack = EVMStack()
    assert len(stack) == 0
    stack.push(1)
    stack.push(2)
    assert len(stack) == 2
    stack.pop()
    assert len(stack) == 1
