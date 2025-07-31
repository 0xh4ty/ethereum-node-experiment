import os
import tempfile
import pytest

from ethereum_node.db.kv import KeyValueDB
from ethereum_node.state.state import State
from ethereum_node.state.account import Account
from ethereum_node.utils.hash import keccak256
from ethereum_node.utils.rlp import encode


@pytest.fixture
def temp_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_state.db")
        db = KeyValueDB(db_path)
        yield State(db)


def test_set_and_get_account(temp_state):
    addr = b'\xaa' * 20
    acct = Account(nonce=1, balance=100, storage_root=keccak256(b""), code_hash=keccak256(b""))
    temp_state.set_account(addr, acct)
    retrieved = temp_state.get_account(addr)
    assert retrieved.nonce == 1
    assert retrieved.balance == 100


def test_transfer(temp_state):
    a = b'\x01' * 20
    b = b'\x02' * 20
    acct_a = Account(nonce=0, balance=500, storage_root=keccak256(b""), code_hash=keccak256(b""))
    acct_b = Account(nonce=0, balance=300, storage_root=keccak256(b""), code_hash=keccak256(b""))
    temp_state.set_account(a, acct_a)
    temp_state.set_account(b, acct_b)
    temp_state.transfer(a, b, 200)
    assert temp_state.get_account(a).balance == 300
    assert temp_state.get_account(b).balance == 500


def test_storage_set_and_get(temp_state):
    addr = b'\x03' * 20
    acct = Account(nonce=0, balance=0, storage_root=keccak256(encode(b"")), code_hash=keccak256(b""))
    temp_state.set_account(addr, acct)
    temp_state.set_storage(addr, b'\x00'*32, b'hello')
    val = temp_state.get_storage(addr, b'\x00'*32)
    assert val == b'hello'


def test_snapshot_and_revert(temp_state):
    addr = b'\x04' * 20
    acct = Account(nonce=0, balance=1000, storage_root=keccak256(encode(b"")), code_hash=keccak256(b""))
    temp_state.set_account(addr, acct)
    snap = temp_state.snapshot()
    temp_state.transfer(addr, b'\x05' * 20, 200)
    assert temp_state.get_account(addr).balance == 800
    temp_state.revert(snap)
    assert temp_state.get_account(addr).balance == 1000


def test_commit(temp_state):
    addr = b'\x06' * 20
    acct = Account(nonce=0, balance=700, storage_root=keccak256(b""), code_hash=keccak256(b""))
    snap = temp_state.snapshot()
    temp_state.set_account(addr, acct)
    temp_state.commit()
    assert temp_state.get_account(addr).balance == 700
