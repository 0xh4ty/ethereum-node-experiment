import os
import tempfile
import pytest

from ethereum_node.db.kv import KeyValueDB
from ethereum_node.state.journal import JournalDB

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test2.db")
        yield KeyValueDB(db_path)

def test_journal_snapshot_revert(temp_db):
    db = JournalDB(temp_db)
    db.set(b"key1", b"val1")
    snap = db.snapshot()
    db.set(b"key1", b"val2")
    db.set(b"key2", b"valB")

    assert db.get(b"key1") == b"val2"
    assert db.get(b"key2") == b"valB"

    db.revert(snap)

    assert db.get(b"key1") == b"val1"
    assert db.get(b"key2") is None

def test_journal_commit(temp_db):
    db = JournalDB(temp_db)
    db.set(b"keyA", b"valX")
    snap = db.snapshot()
    db.set(b"keyA", b"valY")
    db.set(b"keyB", b"valZ")

    db.commit(snap)

    assert db.get(b"keyA") == b"valY"
    assert db.get(b"keyB") == b"valZ"

    # Further revert should not undo committed state
    db.revert(snap)
    assert db.get(b"keyA") == b"valY"
    assert db.get(b"keyB") == b"valZ"

def test_multiple_snapshots(temp_db):
    db = JournalDB(temp_db)
    db.set(b"x", b"1")
    s1 = db.snapshot()

    db.set(b"x", b"2")
    s2 = db.snapshot()

    db.set(b"x", b"3")

    assert db.get(b"x") == b"3"
    db.revert(s2)
    assert db.get(b"x") == b"2"
    db.revert(s1)
    assert db.get(b"x") == b"1"
