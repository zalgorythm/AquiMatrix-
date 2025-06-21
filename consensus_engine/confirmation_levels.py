"""
confirmation_levels.py

Assigns confirmation levels to entries in the DAG, indicating their degree of finality.

Functions:
1. Level Assignment: Starts entries at L=0 on publication.
2. Advances to L=1 when entry is referenced by ≥3 entries at L=0.
3. For L>1, requires ≥3 incoming references from entries at level L-1 and weight threshold.
4. Marks entries as final at high level (e.g., L=3).
"""

from consensus_engine.weight_accumulation import get_weight_at_level
from lib.database_access import update_entry_level, get_entry_references
import logging

from consensus_engine.token_rewards import reward_miner

logger = logging.getLogger('confirmation_levels')

W0 = 3  # base weight
R = 2   # growth factor
FINAL_LEVEL = 3

def weight_threshold(level):
    return W0 * (R ** level)

class ConfirmationLevels:
    def __init__(self, db):
        self.db = db

    def assign_level(self, entry_hash, miner_id=None):
        entry = get_entry_references(self.db, entry_hash)
        current_level = entry.get('level', 0)

        if current_level == 0:
            # Check if referenced by ≥3 entries at L=0
            refs = entry.get('references', [])
            count = sum(1 for r in refs if self.get_entry_level(r) == 0)
            if count >= 3:
                update_entry_level(self.db, entry_hash, 1)
                current_level = 1

        else:
            # For L>1
            next_level = current_level + 1
            refs = entry.get('references', [])
            count = sum(1 for r in refs if self.get_entry_level(r) == current_level)
            weight = get_weight_at_level(self.db, entry_hash, current_level)
            if count >= 3 and weight >= weight_threshold(current_level):
                update_entry_level(self.db, entry_hash, next_level)
                current_level = next_level

        if current_level >= FINAL_LEVEL:
            self.mark_entry_final(entry_hash)
            logger.info(f"Entry {entry_hash} marked as final at level {current_level}")
            # Reward miner when entry is final
            if miner_id and self.db:
                reward_miner(self.db, miner_id)

        return current_level

    def get_entry_level(self, entry_hash):
        entry = get_entry_references(self.db, entry_hash)
        return entry.get('level', 0)

    def mark_entry_final(self, entry_hash):
        # Mark entry as final in database
        logger.info(f"Marking entry {entry_hash} as final")
        # Implementation to update database to mark finality
        pass
