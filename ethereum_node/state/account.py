#!/usr/bin/env python3

from dataclasses import dataclass
from ethereum_node.utils.rlp import encode


@dataclass
class Account:
    nonce: int              # Number of transactions sent
    balance: int            # Wei balance
    storage_root: bytes     # Root of the storage trie (32 bytes)
    code_hash: bytes        # Keccak256 hash of the contract bytecode

    def rlp(self) -> bytes:
        return encode([
            self.nonce,
            self.balance,
            self.storage_root,
            self.code_hash
        ])
