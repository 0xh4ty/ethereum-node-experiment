#!/usr/bin/env python3
# ethereum_node/state/trie.py
#
# Merkle‑Patricia Trie with in‑DB node hashing.
# Fixes:
#   • branch‑value slot now treated as “no value” when it’s b''
#   • empty‑bytes children handled as missing
#   • correct splitting of EXTENSION nodes when a new key diverges
#   • conventional commit suggestion:  fix(trie): keep extension path tail when splitting & treat empty bytes as None
#

from typing import Union, List, Optional, Tuple

from ethereum_node.utils.rlp import encode, decode
from ethereum_node.utils.hash import keccak256
from ethereum_node.db.kv import KeyValueDB

Node = Union[bytes, List["Node"]]            # raw 32‑byte hash or in‑memory node


# ── helpers ──────────────────────────────────────────────────────────────

def bytes_to_nibbles(b: bytes) -> List[int]:
    out: List[int] = []
    for byte in b:
        out.append(byte >> 4)
        out.append(byte & 0x0F)
    return out


def nibbles_to_bytes(nibbles: List[int]) -> bytes:
    if len(nibbles) % 2:
        raise ValueError("Nibble array must have even length")
    buf = bytearray()
    for i in range(0, len(nibbles), 2):
        buf.append((nibbles[i] << 4) | nibbles[i + 1])
    return bytes(buf)


def encode_path(nibbles: List[int], is_leaf: bool) -> bytes:
    """Hex‑prefix encoding (yellow‑paper §4.1)."""
    odd = len(nibbles) & 1
    flags = 0x20 if is_leaf else 0x00
    if odd:
        flags |= 0x10
        return bytes([flags | nibbles[0]]) + nibbles_to_bytes(nibbles[1:])
    return bytes([flags]) + nibbles_to_bytes(nibbles)


def decode_path(path: bytes) -> Tuple[List[int], bool]:
    if not path:
        return [], False
    flag      = path[0]
    is_leaf   = bool(flag & 0x20)
    odd       = bool(flag & 0x10)
    nibbles   = bytes_to_nibbles(path[1:]) if not odd else [flag & 0x0F] + bytes_to_nibbles(path[1:])
    return nibbles, is_leaf


# ── trie ─────────────────────────────────────────────────────────────────

class Trie:
    def __init__(self, db: KeyValueDB):
        self.db   = db
        self.root: Optional[Node] = None

    # ── public API ────────────────────────────────────────────────────

    def get(self, key: bytes) -> Optional[bytes]:
        return self._get(self.root, bytes_to_nibbles(key))

    def update(self, key: bytes, value: bytes) -> None:
        self.root = self._update(self.root, bytes_to_nibbles(key), value)

    def root_hash(self) -> bytes:
        return keccak256(encode(self.root)) if self.root else keccak256(encode(b""))

    # ── internal: lookup ─────────────────────────────────────────────

    def _get(self, node: Optional[Node], key: List[int]) -> Optional[bytes]:
        if node is None or node == b'':
            return None
        if isinstance(node, bytes) and len(node) == 32:
            node = self._resolve(node)

        if len(node) == 2:                          # leaf | extension
            path, is_leaf = decode_path(node[0])
            if key[:len(path)] != path:
                return None
            if is_leaf:
                return node[1] if key == path else None
            return self._get(node[1], key[len(path):])

        if len(node) == 17:                         # branch
            if not key:
                return node[16] if (isinstance(node[16], bytes) and node[16] != b'') else None
            return self._get(node[key[0]], key[1:])

        raise Exception("Invalid node structure")

    # ── internal: insert / update ────────────────────────────────────

    def _update(self, node: Optional[Node], key: List[int], value: bytes) -> Node:
        if not node:                                # empty spot → new leaf
            return self._store_node([encode_path(key, True), value])

        if node == b'':                             # empty child placeholder
            return self._store_node([encode_path(key, True), value])

        if isinstance(node, bytes) and len(node) == 32:
            node = self._resolve(node)

        # ── LEAF / EXTENSION ───────────────────────────────────────
        if len(node) == 2:
            path, is_leaf = decode_path(node[0])

            # common prefix length
            i = 0
            while i < len(path) and i < len(key) and path[i] == key[i]:
                i += 1

            if is_leaf:
                # ── existing LEAF ────────────────────────────────
                if i == len(path) and i == len(key):
                    return self._store_node([encode_path(path, True), value])  # overwrite exact leaf

                branch: List[Node] = [b'' for _ in range(17)]

                # put existing leaf under its diverging nibble / value slot
                if i < len(path):
                    branch[path[i]] = self._store_node([encode_path(path[i + 1:], True), node[1]])
                else:
                    branch[16] = node[1]

                # put new value
                if i < len(key):
                    branch[key[i]] = self._store_node([encode_path(key[i + 1:], True), value])
                else:
                    branch[16] = value

                if i == 0:
                    return self._store_node(branch)
                return self._store_node([encode_path(key[:i], False), self._store_node(branch)])

            # ── EXTENSION ─────────────────────────────────────────
            if i == len(path):
                # full match → recurse into child
                child = self._update(node[1], key[i:], value)
                return self._store_node([encode_path(path, False), child])

            # need to split extension
            branch: List[Node] = [b'' for _ in range(17)]

            # old child behind its next nibble
            old_nibble = path[i]
            old_tail   = path[i + 1:]
            branch[old_nibble] = (
                self._store_node([encode_path(old_tail, False), node[1]]) if old_tail else node[1]
            )

            # new child / value
            if i < len(key):
                new_nibble = key[i]
                branch[new_nibble] = self._store_node([encode_path(key[i + 1:], True), value])
            else:
                branch[16] = value

            branch_node = self._store_node(branch)
            return branch_node if i == 0 else self._store_node([encode_path(path[:i], False), branch_node])

        # ── BRANCH ────────────────────────────────────────────────
        if len(node) == 17:
            if not key:
                node[16] = value
            else:
                node[key[0]] = self._update(node[key[0]], key[1:], value)
            return self._store_node(node)

        raise Exception("Invalid node structure")

    # ── DB helpers ─────────────────────────────────────────────────

    def _resolve(self, child: Node) -> Node:
        raw = self.db.get(child)  # type: ignore[arg-type]
        if raw is None:
            raise ValueError(f"Missing node in DB: {child.hex()}")
        return decode(raw)

    def _store_node(self, node: Node) -> Node:
        encoded = encode(node)
        if len(encoded) < 32:                       # inline if small
            return node
        h = keccak256(encoded)
        self.db.put(h, encoded)
        return h
