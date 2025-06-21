"""
Improved implementation of database_access module with basic file-based persistence.
"""

import json
import os
from threading import Lock

class PersistentDB:
    def __init__(self, filepath='ledger_db.json'):
        self.filepath = filepath
        self.lock = Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            self.entries = data.get('entries', {})
            self.invalid_entries = set(data.get('invalid_entries', []))
            self.token_balances = data.get('token_balances', {})
            self.difficulties = data.get('difficulties', [])
            self.timestamps = data.get('timestamps', [])
            self.vault_balance = data.get('vault_balance', 0)
            self.lrw_balances = data.get('lrw_balances', {})
            self.stake_balances = data.get('stake_balances', {})
            self.staking_rewards = data.get('staking_rewards', {})
        else:
            self.entries = {}
            self.invalid_entries = set()
            self.token_balances = {}
            self.difficulties = []
            self.timestamps = []
            self.vault_balance = 0
            self.lrw_balances = {}
            self.stake_balances = {}
            self.staking_rewards = {}

    def _save(self):
        with self.lock:
            data = {
                'entries': self.entries,
                'invalid_entries': list(self.invalid_entries),
                'token_balances': self.token_balances,
                'difficulties': self.difficulties,
                'timestamps': self.timestamps,
                'vault_balance': self.vault_balance,
                'lrw_balances': self.lrw_balances,
                'stake_balances': self.stake_balances,
                'staking_rewards': self.staking_rewards,
            }
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)

db_instance = PersistentDB()

def get_stake(db, entry_hash):
    return getattr(db, 'stakes', {}).get(entry_hash, 0)

def mark_invalid(db, entry_hash):
    if hasattr(db, 'invalid_entries'):
        db.invalid_entries.add(entry_hash)
        db._save()

def get_token_balance(db, miner_id):
    return getattr(db, 'token_balances', {}).get(miner_id, 0)

def store_token_balance(db, miner_id, balance):
    if hasattr(db, 'token_balances'):
        db.token_balances[miner_id] = balance
        db._save()

def get_vault_balance(db):
    return getattr(db, 'vault_balance', 0)

def store_vault_balance(db, balance):
    setattr(db, 'vault_balance', balance)
    db._save()

def get_lrw_balance(db, user_id):
    return getattr(db, 'lrw_balances', {}).get(user_id, 0)

def store_lrw_balance(db, user_id, balance):
    if not hasattr(db, 'lrw_balances'):
        db.lrw_balances = {}
    db.lrw_balances[user_id] = balance
    db._save()

def get_stake_balance(db, user_id):
    return getattr(db, 'stake_balances', {}).get(user_id, 0)

def store_stake_balance(db, user_id, balance):
    if not hasattr(db, 'stake_balances'):
        db.stake_balances = {}
    db.stake_balances[user_id] = balance
    db._save()

def get_staking_rewards(db, user_id):
    return getattr(db, 'staking_rewards', {}).get(user_id, 0)

def store_staking_rewards(db, user_id, amount):
    if not hasattr(db, 'staking_rewards'):
        db.staking_rewards = {}
    db.staking_rewards[user_id] = amount
    db._save()

def get_last_m_timestamps(db, m):
    if hasattr(db, 'timestamps'):
        return db.timestamps[-m:]
    return []

def store_difficulty(db, current_target, k, delta):
    if hasattr(db, 'difficulties'):
        db.difficulties.append({'target': current_target, 'k': k, 'delta': delta})
        db._save()

def check_entry_exists(db, entry_hash):
    if hasattr(db, 'entries'):
        return entry_hash in db.entries
    return False

def store_entry(db, entry_hash, entry):
    if hasattr(db, 'entries'):
        db.entries[entry_hash] = entry
        db._save()

def get_entry(db, entry_hash):
    if hasattr(db, 'entries'):
        return db.entries.get(entry_hash)
    return None

def entry_exists(db, entry_hash):
    return check_entry_exists(db, entry_hash)

def update_entry_level(db, entry_hash, level):
    if hasattr(db, 'entries') and entry_hash in db.entries:
        db.entries[entry_hash]['level'] = level
        db._save()

def get_entry_references(db, entry_hash):
    entry = get_entry(db, entry_hash)
    if entry:
        return {
            'level': entry.get('level', 0),
            'references': entry.get('references', [])
        }
    return {
        'level': 0,
        'references': []
    }
