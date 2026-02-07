#!/usr/bin/env python3
"""
High-level World-State façade.
* keeps a Merkle-Patricia-Trie of accounts
* wraps a `JournalDB` so every change can be snapshotted / reverted
* exposes helpers for balance transfers and contract storage
"""
from typing import Optional, Dict
from ethereum_node.utils.rlp import encode, decode
from ethereum_node.utils.hash import keccak256
from ethereum_node.db.kv import KeyValueDB
from ethereum_node.state.journal import JournalDB
from ethereum_node.state.trie import Trie
from ethereum_node.state.account import Account
# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def _decode_int(b: bytes) -> int:
    """Ethereum RLP encodes integers big-endian; empty byte-string == 0."""
    return int.from_bytes(b, "big") if b else 0
# --------------------------------------------------------------------------- #
# State object
# --------------------------------------------------------------------------- #
class State:
    """Top-level container for accounts and contract storage."""
    def __init__(self, db: KeyValueDB):
        # Wrap the real KV-store with a journalling layer
        self.journal: JournalDB = JournalDB(db)
        # The account-trie itself stores keys/values inside that journal
        self.trie:    Trie      = Trie(self.journal)
        # Track root snapshots for journalling
        self._root_snaps: Dict[int, bytes] = {}
    # ------------------------------ accounts --------------------------------
    def get_account(self, address: bytes) -> Optional[Account]:
        encoded = self.trie.get(address)
        if not encoded:
            return None
        fields = decode(encoded)
        return Account(
            nonce        = _decode_int(fields[0]),
            balance      = _decode_int(fields[1]),
            storage_root = fields[2],
            code_hash    = fields[3],
        )
    def set_account(self, address: bytes, account: Account) -> None:
        self.trie.update(address, account.rlp())
    # ------------------------------- ETH ------------------------------------
    def transfer(self, sender: bytes, recipient: bytes, amount: int) -> None:
        # if an address is missing we treat it as an empty EOA
        empty_root = keccak256(encode(b""))
        empty_acct = Account(0, 0, empty_root, keccak256(b""))
        sender_acct    = self.get_account(sender)    or empty_acct
        recipient_acct = self.get_account(recipient) or empty_acct
        assert sender_acct.balance >= amount, "Insufficient funds"
        sender_acct.balance    -= amount
        recipient_acct.balance += amount
        self.set_account(sender,    sender_acct)
        self.set_account(recipient, recipient_acct)
    # ------------------------------ storage ---------------------------------
    def _storage_trie(self, root: bytes) -> Trie:
        """Return a storage-trie *view* rooted at `root`."""
        return Trie(self.journal, root=root)
    def get_storage(self, address: bytes, slot: bytes) -> bytes:
        """Get a storage slot for an account."""
        account = self.get_account(address)
        if account is None:
            return b""
        # Create storage trie with the account's current storage root
        storage_trie = Trie(self.journal, root=account.storage_root)
        return storage_trie.get(slot) or b""
    def set_storage(self, address: bytes, slot: bytes, value: bytes) -> None:
        """Set a storage slot for an account."""
        account = self.get_account(address)
        if account is None:
            raise ValueError(f"Account {address.hex()} does not exist")
        # Create storage trie with current storage root
        storage_trie = Trie(self.journal, root=account.storage_root)
        # Update the storage
        storage_trie.update(slot, value)
        # CRITICAL: Update the account with the new storage root
        updated_account = Account(
            nonce=account.nonce,
            balance=account.balance,
            storage_root=storage_trie.root,  # Use the updated trie root
            code_hash=account.code_hash
        )
        self.set_account(address, updated_account)
    # --------------------------- journalling --------------------------------
    def snapshot(self) -> int:
        """Return a snapshot-id that can later be reverted or committed."""
        snap_id = self.journal.snapshot()
        self._root_snaps[snap_id] = self.trie.root
        return snap_id
    def revert(self, snapshot_id: int) -> None:
        # restore key-value layer **and** the root pointer
        self.journal.revert(snapshot_id)
        self.trie.root = self._root_snaps.pop(snapshot_id, None)
    def commit(self, snapshot_id: Optional[int] = None) -> None:
        """
        Persist changes in the journal:
        * if `snapshot_id` given → commit up to that id
        * else commit **all** outstanding changes
        """
        if snapshot_id is None:
            if not self.journal._snapshots:
                return                       # nothing to do
            snapshot_id = self.journal._snapshots[-1]
        self.journal.commit(snapshot_id)
        self._root_snaps = {sid: root for sid, root in self._root_snaps.items()
                            if sid > snapshot_id}
