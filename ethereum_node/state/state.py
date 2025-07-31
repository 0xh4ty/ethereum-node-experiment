#!/usr/bin/env python3
# ethereum_node/state/state.py

from typing import Optional
from ethereum_node.db.kv import KeyValueDB
from ethereum_node.state.journal import JournalDB
from ethereum_node.state.trie import Trie
from ethereum_node.state.account import Account
from ethereum_node.utils.rlp import encode, decode
from ethereum_node.utils.hash import keccak256


class State:
    def __init__(self, db: KeyValueDB):
        self.journal = JournalDB(db)
        self.trie = Trie(self.journal)

    def get_account(self, address: bytes) -> Optional[Account]:
        encoded = self.trie.get(address)
        if not encoded:
            return None
        fields = decode(encoded)
        return Account(
            nonce=int(fields[0]),
            balance=int(fields[1]),
            storage_root=fields[2],
            code_hash=fields[3]
        )

    def set_account(self, address: bytes, account: Account) -> None:
        self.trie.update(address, account.rlp())

    def transfer(self, sender: bytes, recipient: bytes, amount: int) -> None:
        sender_acct = self.get_account(sender) or Account(0, 0, keccak256(encode(b"")), keccak256(b""))
        recipient_acct = self.get_account(recipient) or Account(0, 0, keccak256(encode(b"")), keccak256(b""))

        assert sender_acct.balance >= amount, "Insufficient funds"

        sender_acct.balance -= amount
        recipient_acct.balance += amount

        self.set_account(sender, sender_acct)
        self.set_account(recipient, recipient_acct)

    def get_storage_trie(self, storage_root: bytes) -> Trie:
        return Trie(self.journal, root=storage_root)

    def get_storage(self, address: bytes, slot: bytes) -> bytes:
        acct = self.get_account(address)
        if not acct:
            return b""
        storage = self.get_storage_trie(acct.storage_root)
        return storage.get(slot) or b""

    def set_storage(self, address: bytes, slot: bytes, value: bytes) -> None:
        acct = self.get_account(address)
        if not acct:
            raise Exception("Account does not exist")

        storage = self.get_storage_trie(acct.storage_root)
        storage.update(slot, value)
        acct.storage_root = storage.root_hash()
        self.set_account(address, acct)

    def snapshot(self) -> int:
        return self.journal.snapshot()

    def revert(self, snap: int) -> None:
        self.journal.revert(snap)

    def commit(self) -> None:
        self.journal.commit()
