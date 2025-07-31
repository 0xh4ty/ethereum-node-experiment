#!/usr/bin/env python3

class JournaledStorage:
    def __init__(self):
        self._store = {}         # persistent state: key → value
        self._original = {}      # original value before any change (used for journaling)
        self._touched = set()    # keys that have been modified in the current transaction

    def load(self, key: int) -> int:
        return self._store.get(key, 0)

    def store(self, key: int, value: int):
        if key not in self._original:
            self._original[key] = self._store.get(key, 0)
        self._store[key] = value
        self._touched.add(key)

    def snapshot(self):
        """Returns a snapshot of the current state."""
        return self._store.copy(), self._original.copy(), self._touched.copy()

    def revert(self):
        """Reverts all changes made since the beginning (for now, full revert)."""
        for key in self._touched:
            original = self._original[key]
            if original == 0:
                self._store.pop(key, None)
            else:
                self._store[key] = original
        self._original.clear()
        self._touched.clear()

    def commit(self):
        """Commits all changes (clears the journal)."""
        self._original.clear()
        self._touched.clear()
