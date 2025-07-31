#!/usr/bin/env python3

import pytest
from ethereum_node.evm.storage import JournaledStorage


def test_storage_load_defaults_to_zero():
    storage = JournaledStorage()
    assert storage.load(0x01) == 0
    assert storage.load(0xABCDEF) == 0


def test_storage_store_and_load():
    storage = JournaledStorage()
    storage.store(0x10, 0x1234)
    assert storage.load(0x10) == 0x1234


def test_storage_revert_restores_original_values():
    storage = JournaledStorage()
    storage.store(0x01, 0xAAAA)
    storage.store(0x02, 0xBBBB)
    storage.store(0x01, 0xCCCC)  # overwrite

    storage.revert()

    assert storage.load(0x01) == 0
    assert storage.load(0x02) == 0


def test_storage_commit_clears_journal():
    storage = JournaledStorage()
    storage.store(0x01, 0xAAAA)
    storage.commit()
    storage.store(0x01, 0xBBBB)
    storage.revert()  # Should revert only most recent change

    assert storage.load(0x01) == 0xAAAA


def test_storage_multiple_keys_revert_and_commit():
    storage = JournaledStorage()
    storage.store(0x01, 0x1111)
    storage.store(0x02, 0x2222)
    storage.commit()

    storage.store(0x01, 0xAAAA)
    storage.store(0x02, 0xBBBB)
    storage.revert()

    assert storage.load(0x01) == 0x1111
    assert storage.load(0x02) == 0x2222
