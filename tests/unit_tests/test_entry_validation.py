"""
test_entry_validation.py

Unit tests for data_ingestion.entry_validator module.
Tests:
- Schema validation with valid and invalid entries.
- Signature verification with valid and invalid signatures.
- Timestamp validation for acceptable and out-of-range timestamps.
- Duplicate detection with mocked database.
"""

import unittest
from unittest.mock import MagicMock
from data_ingestion.entry_validator import EntryValidator

class TestEntryValidator(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.validator = EntryValidator(self.mock_db)

    def test_validate_schema_valid(self):
        entry = {
            'timestamp': 1234567890,
            'predecessor_hashes': ['a', 'b', 'c'],
            'transaction_data': {},
            'signature': 'sig',
            'submitter_public_key': 'key'
        }
        valid, msg = self.validator.validate_schema(entry)
        self.assertTrue(valid)

    def test_validate_schema_missing_field(self):
        entry = {
            'timestamp': 1234567890,
            'predecessor_hashes': ['a', 'b', 'c'],
            'transaction_data': {},
            'signature': 'sig'
        }
        valid, msg = self.validator.validate_schema(entry)
        self.assertFalse(valid)
        self.assertIn('Missing required field', msg)

    def test_validate_signature_invalid(self):
        entry = {
            'timestamp': 1234567890,
            'predecessor_hashes': ['a', 'b', 'c'],
            'transaction_data': {},
            'signature': 'bad_sig',
            'submitter_public_key': 'key'
        }
        # Patch verify_signature to return False
        self.validator.validate_signature = lambda e: (False, "Invalid signature")
        valid, msg = self.validator.validate_signature(entry)
        self.assertFalse(valid)

    def test_validate_timestamp_out_of_range(self):
        import time
        entry = {
            'timestamp': time.time() + 10000,
            'predecessor_hashes': ['a', 'b', 'c'],
            'transaction_data': {},
            'signature': 'sig',
            'submitter_public_key': 'key'
        }
        valid, msg = self.validator.validate_timestamp(entry)
        self.assertFalse(valid)

    def test_check_duplicate_true(self):
        self.mock_db.entry_exists.return_value = True
        valid, msg = self.validator.check_duplicate('hash')
        self.assertFalse(valid)

    def test_check_duplicate_false(self):
        self.mock_db.entry_exists.return_value = False
        valid, msg = self.validator.check_duplicate('hash')
        self.assertTrue(valid)

if __name__ == '__main__':
    unittest.main()
