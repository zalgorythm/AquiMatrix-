"""
entry_validator.py

Responsible for the initial validation of all incoming entries submitted to the AquiMatrix network.
Performs multi-step validation:
1. Schema Validation: Ensures the entry adheres to a predefined structure (e.g., contains required fields like timestamp, predecessor hashes, transaction data, and signature).
2. Signature Verification: Uses the cryptographic_functions.py library to verify the ECDSA signature against the submitter’s public key, ensuring authenticity and integrity.
3. Timestamp Check: Confirms the timestamp is within an acceptable range (e.g., not too far in the future or past relative to the node’s clock, adjusted for network latency).
4. Duplicate Detection: Checks against the database (via database_access.py) to prevent reprocessing of already-seen entries.
If any check fails, the entry is rejected with an error code, logged, and reported back to the submitter via the API.
This file is critical for maintaining the system’s security and data integrity at the ingestion layer.
"""

import json
import time
from lib.cryptographic_functions import verify_signature
from lib.database_access import check_entry_exists

class EntryValidator:
    REQUIRED_FIELDS = ['timestamp', 'predecessor_hashes', 'transaction_data', 'signature', 'submitter_public_key']

    def __init__(self, db):
        self.db = db

    def validate_schema(self, entry):
        for field in self.REQUIRED_FIELDS:
            if field not in entry:
                return False, f"Missing required field: {field}"
        if not isinstance(entry['predecessor_hashes'], list) or len(entry['predecessor_hashes']) != 3:
            return False, "predecessor_hashes must be a list of exactly 3 hashes"
        return True, "Schema valid"

    def validate_signature(self, entry):
        data_to_sign = json.dumps({
            'timestamp': entry['timestamp'],
            'predecessor_hashes': entry['predecessor_hashes'],
            'transaction_data': entry['transaction_data']
        }, sort_keys=True)
        signature = entry['signature']
        public_key = entry['submitter_public_key']
        # Adjusted to match verify_signature signature in cryptographic_functions.py
        valid, msg = verify_signature(entry)
        if not valid:
            return False, "Invalid signature"
        return True, "Signature valid"

    def validate_timestamp(self, entry):
        current_time = time.time()
        timestamp = entry['timestamp']
        # Acceptable range: within 5 minutes in past or future
        if timestamp < current_time - 300 or timestamp > current_time + 300:
            return False, "Timestamp out of acceptable range"
        return True, "Timestamp valid"

    def check_duplicate(self, entry_hash):
        if check_entry_exists(self.db, entry_hash):
            return False, "Duplicate entry"
        return True, "Entry is unique"

    def validate_entry(self, entry, entry_hash):
        valid, msg = self.validate_schema(entry)
        if not valid:
            return False, msg
        valid, msg = self.validate_signature(entry)
        if not valid:
            return False, msg
        valid, msg = self.validate_timestamp(entry)
        if not valid:
            return False, msg
        valid, msg = self.check_duplicate(entry_hash)
        if not valid:
            return False, msg
        return True, "Entry validation successful"
