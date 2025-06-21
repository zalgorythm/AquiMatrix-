"""
conflict_resolver.py

Resolves conflicts in the DAG, such as double-spends, by selecting the most trusted branch.
Features:
1. Conflict Detection: Identifies conflicting entries via transaction payload analysis.
2. Branch Scoring: Computes score based on accumulated weight and economic stake.
3. Resolution: Selects branch with highest score, marks losing branch invalid.
4. Logging: Records resolution decisions for auditability.
Interacts with dag_structure.py and state_trie.py.
"""

from consensus_engine.weight_accumulation import get_accumulated_weight
from lib import database_access
import logging
from consensus_engine.audit_report import setup_audit_logger

logger = logging.getLogger('conflict_resolver')
audit_logger = setup_audit_logger()

class ConflictResolver:
    def __init__(self, db):
        self.db = db

    def detect_conflicts(self, entries):
        """
        Detect conflicting entries (e.g., double spends).
        :param entries: list of entries to check
        :return: list of conflict groups
        """
        conflicts = []
        # Simple example implementation:
        # Group entries by transaction outputs that conflict
        output_to_entries = {}
        for entry in entries:
            outputs = entry.get('transaction_data', {}).get('outputs', [])
            for output in outputs:
                if output in output_to_entries:
                    output_to_entries[output].append(entry['hash'])
                else:
                    output_to_entries[output] = [entry['hash']]
        # Find outputs with more than one entry (conflicts)
        for output, entry_hashes in output_to_entries.items():
            if len(entry_hashes) > 1:
                conflicts.append(entry_hashes)
        return conflicts

    def score_branch(self, entry_hash):
        """
        Compute score for a branch based on accumulated weight and stake.
        """
        weight = get_accumulated_weight(self.db, entry_hash)
        stake = database_access.get_stake(self.db, entry_hash)
        audit_logger.info(f"Scoring branch {entry_hash} with weight {weight} and stake {stake}")
        return weight + stake

    def resolve_conflicts(self, conflict_groups):
        """
        Resolve conflicts by selecting highest scoring branch.
        """
        for group in conflict_groups:
            scores = {entry_hash: self.score_branch(entry_hash) for entry_hash in group}
            winner = max(scores, key=scores.get)
            for entry_hash in group:
                if entry_hash != winner:
                    database_access.mark_invalid(self.db, entry_hash)
                    logger.info(f"Entry {entry_hash} marked invalid due to conflict resolution")
                    audit_logger.info(f"Entry {entry_hash} marked invalid due to conflict resolution")
            logger.info(f"Conflict resolved, winner: {winner}")
            audit_logger.info(f"Conflict resolved, winner: {winner}")
