#!/usr/bin/env python3
import os
import tempfile
import pytest

from ethereum_node.db.kv import KeyValueDB
from ethereum_node.state.state import State
from ethereum_node.state.account import Account
from ethereum_node.utils.hash import keccak256
from ethereum_node.utils.rlp import encode


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def temp_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "world.db")
        db      = KeyValueDB(db_path)
        yield State(db)


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #

def test_set_and_get_account(temp_state):
    addr = b"\xaa" * 20
    acct = Account(1, 100, keccak256(b""), keccak256(b""))
    temp_state.set_account(addr, acct)

    retrieved = temp_state.get_account(addr)
    assert retrieved is not None
    assert retrieved.nonce   == 1
    assert retrieved.balance == 100


def test_transfer(temp_state):
    a = b"\x01" * 20
    b = b"\x02" * 20

    temp_state.set_account(a, Account(0, 500, keccak256(b""), keccak256(b"")))
    temp_state.set_account(b, Account(0, 300, keccak256(b""), keccak256(b"")))

    temp_state.transfer(a, b, 200)

    assert temp_state.get_account(a).balance == 300
    assert temp_state.get_account(b).balance == 500


def test_storage_set_and_get(temp_state):
    addr = b"\x03" * 20
    empty_root = keccak256(encode(b""))
    temp_state.set_account(addr, Account(0, 0, empty_root, keccak256(b"")))

    slot = b"\x00" * 32
    temp_state.set_storage(addr, slot, b"hello")
    assert temp_state.get_storage(addr, slot) == b"hello"


def test_snapshot_and_revert(temp_state):
    addr = b"\x04" * 20
    temp_state.set_account(addr, Account(0, 1_000, keccak256(encode(b"")), keccak256(b"")))

    snap = temp_state.snapshot()
    temp_state.transfer(addr, b"\x05" * 20, 250)
    assert temp_state.get_account(addr).balance == 750

    temp_state.revert(snap)
    assert temp_state.get_account(addr).balance == 1_000


def test_commit(temp_state):
    addr = b"\x06" * 20
    temp_state.snapshot()                                # create snap-id = 1
    temp_state.set_account(addr, Account(0, 700, keccak256(b""), keccak256(b"")))
    temp_state.commit()                                  # commit latest snapshot

    # after commit, the account should still be accessible
    assert temp_state.get_account(addr).balance == 700
