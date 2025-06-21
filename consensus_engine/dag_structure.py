"""
dag_structure.py

Maintains the Directed Acyclic Graph (DAG) that serves as AquiMatrix’s ledger.

Functions:
1. Entry Addition: Adds new entries referencing exactly three valid predecessors.
2. Acyclicity: Enforces directed, acyclic structure by validating timestamps.
3. Graph Integrity: Uses database to store DAG and detect orphaned or invalid references.
4. Traversal: Provides functions for traversing DAG to compute weights or resolve conflicts.
"""

from lib.database_access import store_entry, get_entry, entry_exists
import time
import logging

logger = logging.getLogger('dag_structure')

from lib.database_access import store_entry, get_entry, entry_exists
import time
import logging

logger = logging.getLogger('dag_structure')

class DAG:
    def __init__(self, db):
        self.db = db
        self.entries = {}  # key: entry hash, value: entry data
        self.tips = set()  # entries with no successors

    def add_entry(self, entry):
        # Validate predecessors
        predecessors = entry.get('predecessor_hashes', [])
        if len(predecessors) != 3:
            logger.error("Entry must reference exactly 3 predecessors")
            raise ValueError("Entry must reference exactly 3 predecessors")

        # Check acyclicity by timestamp
        entry_timestamp = entry.get('timestamp')
        for p_hash in predecessors:
            p_entry = get_entry(self.db, p_hash)
            if p_entry is None:
                logger.error(f"Predecessor {p_hash} not found")
                raise ValueError(f"Predecessor {p_hash} not found")
            if p_entry['timestamp'] >= entry_timestamp:
                logger.error("Predecessor timestamp must be less than entry timestamp")
                raise ValueError("Predecessor timestamp must be less than entry timestamp")

        entry_hash = entry.get('hash')
        if entry_exists(self.db, entry_hash):
            logger.error("Entry already exists")
            raise ValueError("Entry already exists")

        # Store entry
        store_entry(self.db, entry_hash, entry)
        self.entries[entry_hash] = entry

        # Update tips
        for p_hash in predecessors:
            if p_hash in self.tips:
                self.tips.remove(p_hash)
        self.tips.add(entry_hash)

    def get_tips(self):
        return list(self.tips)

    def traverse(self, start_hash, visit_func):
        visited = set()
        stack = [start_hash]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            entry = self.entries.get(current)
            if entry is None:
                continue
            visit_func(entry)
            for p_hash in entry.get('predecessor_hashes', []):
                stack.append(p_hash)
