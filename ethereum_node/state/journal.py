#!/usr/bin/env python3

from typing import Any, Dict, List, Tuple, Optional
from ethereum_node.db.kv import KeyValueDB

class JournalDB:
    def __init__(self, db: KeyValueDB):
        self.db = db
        self._journal: List[Tuple[int, bytes, Optional[bytes]]] = []
        self._snapshots: List[int] = []
        self._current_snapshot_id = 0
        self._cache: Dict[bytes, Optional[bytes]] = {}

    def get(self, key: bytes) -> Optional[bytes]:
        if key in self._cache:
            return self._cache[key]
        return self.db.get(key)

    def put(self, key: bytes, value: bytes) -> None:
        old_value = self.get(key)
        self._journal.append((self._current_snapshot_id, key, old_value))
        self._cache[key] = value

    def delete(self, key: bytes) -> None:
        old_value = self.get(key)
        self._journal.append((self._current_snapshot_id, key, old_value))
        self._cache[key] = None

    def set(self, key: bytes, value: bytes):
        self.put(key, value)

    def snapshot(self) -> int:
        self._current_snapshot_id += 1
        self._snapshots.append(self._current_snapshot_id)
        return self._current_snapshot_id

    def revert(self, snapshot_id: int):
        while self._journal and self._journal[-1][0] >= snapshot_id:
            _, key, old_value = self._journal.pop()
            if old_value is None:
                self._cache.pop(key, None)
            else:
                self._cache[key] = old_value
        self._snapshots = [id for id in self._snapshots if id < snapshot_id]

    def commit(self, snapshot_id: int):
        for snap, key, _ in self._journal:
            if snap <= snapshot_id and key in self._cache:
                val = self._cache[key]
                if val is None:
                    self.db.delete(key)
                else:
                    self.db.put(key, val)
        self._journal = [entry for entry in self._journal if entry[0] > snapshot_id]
        self._snapshots = [id for id in self._snapshots if id > snapshot_id]
