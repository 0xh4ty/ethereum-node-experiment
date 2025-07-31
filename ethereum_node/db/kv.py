#!/usr/bin/env python3
# db/kv.py

import sqlite3
from typing import Optional


class KeyValueDB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (k BLOB PRIMARY KEY, v BLOB)"
            )

    def get(self, key: bytes) -> Optional[bytes]:
        cursor = self.conn.execute("SELECT v FROM kv WHERE k = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def put(self, key: bytes, value: bytes):
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)", (key, value))

    def delete(self, key: bytes):
        with self.conn:
            self.conn.execute("DELETE FROM kv WHERE k = ?", (key,))

    def close(self):
        self.conn.close()
