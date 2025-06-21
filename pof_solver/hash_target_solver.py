"""
hash_target_solver.py

Implements the core hash-target puzzle of the Proof of Fractal (PoF) consensus mechanism.

Functions:
1. Aggregate Hash Computation: Combines entry data into an aggregate hash using SHA-256.
2. Nonce Iteration: Appends nonce to aggregate hash and computes final hash, iterating nonce until result is below target.
3. Target Validation: Compares final hash against current difficulty target.

Logs computational effort for monitoring and debugging.
"""

import hashlib
import json
import logging
import os

# Load pof_parameters from JSON config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'pof_parameters.json')
with open(config_path, 'r') as f:
    pof_parameters = json.load(f)

logger = logging.getLogger('pof_solver')

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def compute_aggregate_hash(predecessor_hashes, timestamp, transaction_data, state_root):
    """
    Compute aggregate hash H_agg = H(H(P1) || H(P2) || H(P3) || T_E || D_E || S_E)
    """
    concat_data = b''.join(predecessor_hashes) + \
                  int(timestamp).to_bytes(8, 'big') + \
                  json.dumps(transaction_data, sort_keys=True).encode('utf-8') + \
                  state_root
    return sha256(concat_data)

def compute_final_hash(aggregate_hash, nonce):
    """
    Compute final hash H_f = H(H_agg || N_E)
    """
    nonce_bytes = nonce.to_bytes(8, 'big')
    return sha256(aggregate_hash + nonce_bytes)

def solve_pof(predecessor_hashes, timestamp, transaction_data, state_root, target, miner_id=None, db=None):
    """
    Iterate nonce to find final hash below target.
    Returns nonce and final hash if found, else None.
    If miner_id and db are provided, record token reward for miner.
    """
    aggregate_hash = compute_aggregate_hash(predecessor_hashes, timestamp, transaction_data, state_root)
    nonce = 0
    max_nonce = 2**64 - 1
    while nonce <= max_nonce:
        final_hash = compute_final_hash(aggregate_hash, nonce)
        final_hash_int = int.from_bytes(final_hash, 'big')
        if final_hash_int < target:
            logger.info(f"PoF solved with nonce {nonce}")
            # Reward miner if info available
            if miner_id and db:
                from consensus_engine.token_rewards import reward_miner
                reward_miner(db, miner_id)
            return nonce, final_hash
        nonce += 1
        if nonce % 100000 == 0:
            logger.debug(f"Nonce iteration at {nonce}")
    logger.warning("PoF solve failed: nonce exhausted")
    return None, None
