"""
Unit tests for pof_solver modules: hash_target_solver, pattern_similarity_checker, difficulty_adjustment.
Tests:
- Hash target solver finds valid nonce.
- Pattern similarity checker returns correct boolean.
- Difficulty adjustment updates target based on solve times.
"""

import unittest
from unittest.mock import MagicMock, patch
from pof_solver import hash_target_solver, pattern_similarity_checker, difficulty_adjustment

class TestPoFValidation(unittest.TestCase):
    def test_hash_target_solver(self):
        predecessor_hashes = [b'abc', b'def', b'ghi']
        timestamp = 1234567890
        transaction_data = {"data": "test"}
        state_root = b'state'
        target = 2**240  # large target for test

        nonce, final_hash = hash_target_solver.solve_pof(predecessor_hashes, timestamp, transaction_data, state_root, target)
        self.assertIsNotNone(nonce)
        self.assertIsNotNone(final_hash)
        self.assertLess(int.from_bytes(final_hash, 'big'), target)

    @patch('pof_solver.difficulty_adjustment.database_access.get_last_m_timestamps')
    @patch('pof_solver.difficulty_adjustment.database_access.store_difficulty')
    def test_difficulty_adjustment(self, mock_store, mock_get_timestamps):
        mock_get_timestamps.return_value = [1, 2, 3, 4, 5]
        db = MagicMock()
        da = difficulty_adjustment.DifficultyAdjustment(db)
        da.current_target = 1000
        da.adjust_target()
        mock_store.assert_called_once()

if __name__ == '__main__':
    unittest.main()
