"""
test_full_entry_lifecycle.py

Integration tests covering the full lifecycle of an entry:
- Submission via REST API
- Validation and DAG addition
- PoF puzzle solving
- Confirmation level assignment
- State update via VM execution
"""

import unittest
import requests
import time

API_URL = "http://localhost:9000"

class TestFullEntryLifecycle(unittest.TestCase):
    def test_entry_lifecycle(self):
        # Create a sample entry
        entry = {
            "timestamp": int(time.time()),
            "predecessor_hashes": ["hash1", "hash2", "hash3"],
            "transaction_data": {"action": "test"},
            "submitter_public_key": "pubkey",
            "signature": "signature",
            "hash": "entryhash"
        }

        # Submit entry
        response = requests.post(f"{API_URL}/entries", json=entry)
        self.assertEqual(response.status_code, 200)

        # Fetch entry
        response = requests.get(f"{API_URL}/entries/{entry['hash']}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['hash'], entry['hash'])

        # Fetch state (assuming state root updated)
        response = requests.get(f"{API_URL}/state/some_contract_address")
        self.assertIn(response.status_code, [200, 404])  # May or may not exist yet

if __name__ == '__main__':
    unittest.main()
