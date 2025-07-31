#!/usr/bin/env python3

#!/usr/bin/env python3

from dataclasses import dataclass
from ethereum_node.utils.rlp import encode
from ethereum_node.utils.hash import keccak256

@dataclass
class BlockHeader:
    parent_hash: bytes
    ommers_hash: bytes
    coinbase: bytes
    state_root: bytes
    transactions_root: bytes
    receipts_root: bytes
    logs_bloom: bytes
    difficulty: int
    number: int
    gas_limit: int
    gas_used: int
    timestamp: int
    extra_data: bytes
    mix_hash: bytes
    nonce: bytes

    def rlp(self):
        return encode([
            self.parent_hash,
            self.ommers_hash,
            self.coinbase,
            self.state_root,
            self.transactions_root,
            self.receipts_root,
            self.logs_bloom,
            self.difficulty,
            self.number,
            self.gas_limit,
            self.gas_used,
            self.timestamp,
            self.extra_data,
            self.mix_hash,
            self.nonce,
        ])

    def hash(self):
        return keccak256(self.rlp())
