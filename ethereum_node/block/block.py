#!/usr/bin/env python3

from typing import List
from ethereum_node.block.header import BlockHeader
from ethereum_node.utils.rlp import encode


class Block:
    def __init__(self, header: BlockHeader, transactions: List[bytes], uncles: List[BlockHeader]):
        self.header = header
        self.transactions = transactions
        self.uncles = uncles

    def rlp(self) -> bytes:
        return encode([
            self.header.rlp(),
            [tx for tx in self.transactions],
            [uncle.rlp() for uncle in self.uncles]
        ])
