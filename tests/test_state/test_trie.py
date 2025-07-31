import tempfile
import os
import pytest
from ethereum_node.state.trie import Trie
from ethereum_node.db.kv import KeyValueDB  # Adjust path if needed

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        yield KeyValueDB(db_path)

def test_insert_and_get_single_key(temp_db):
    trie = Trie(temp_db)
    trie.update(b"dog", b"puppy")
    assert trie.get(b"dog") == b"puppy"

def test_overwrite_key(temp_db):
    trie = Trie(temp_db)
    trie.update(b"dog", b"puppy")
    trie.update(b"dog", b"canine")
    assert trie.get(b"dog") == b"canine"

def test_insert_and_retrieve_multiple_keys(temp_db):
    trie = Trie(temp_db)
    trie.update(b"dog", b"puppy")
    trie.update(b"do", b"verb")
    trie.update(b"cat", b"kitten")
    trie.update(b"fish", b"fishlet")
    assert trie.get(b"dog") == b"puppy"
    assert trie.get(b"fish") == b"fishlet"
    assert trie.get(b"do") == b"verb"
    assert trie.get(b"cat") == b"kitten"
    assert trie.get(b"cow") is None

def test_empty_key(temp_db):
    trie = Trie(temp_db)
    trie.update(b"", b"empty")
    assert trie.get(b"") == b"empty"

def test_long_common_prefix(temp_db):
    trie = Trie(temp_db)
    trie.update(b"abcdef", b"val1")
    trie.update(b"abcxyz", b"val2")
    assert trie.get(b"abcdef") == b"val1"
    assert trie.get(b"abcxyz") == b"val2"
    assert trie.get(b"abc") is None
