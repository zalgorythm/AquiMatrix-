"""
pattern_similarity_checker.py

Enforces the bit-pattern similarity condition unique to the PoF validation process.

Functions:
1. Predecessor Hash Aggregation: Computes SHA-256 hash of concatenated predecessor hashes.
2. XOR Operation: Calculates bitwise XOR between final hash and predecessor hash aggregation.
3. Hamming Distance Check: Computes Hamming distance between prefix_k(X) and suffix_k(predecessor hash).
4. Threshold Validation: Ensures Hamming distance is below mismatch tolerance δ.
"""

import hashlib
import json
import os

# Load pof_parameters from JSON config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'pof_parameters.json')
with open(config_path, 'r') as f:
    pof_parameters = json.load(f)

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def hamming_distance(a: bytes, b: bytes) -> int:
    """Compute the Hamming distance between two byte strings."""
    assert len(a) == len(b)
    distance = 0
    for x, y in zip(a, b):
        diff = x ^ y
        distance += bin(diff).count('1')
    return distance

def check_pattern_condition(final_hash: bytes, predecessor_hashes: list) -> bool:
    """
    Check if the pattern condition passes.
    """
    concatenated_predecessors = b''.join(predecessor_hashes)
    predecessor_hash = sha256(concatenated_predecessors)
    X = xor_bytes(final_hash, predecessor_hash)

    k_bits = pof_parameters['bit_length']
    delta = pof_parameters['mismatch_tolerance']

    # Convert bytes to bits
    def bytes_to_bits(b):
        return ''.join(f'{byte:08b}' for byte in b)

    X_bits = bytes_to_bits(X)
    pred_bits = bytes_to_bits(predecessor_hash)

    prefix_k = X_bits[:k_bits]
    suffix_k = pred_bits[-k_bits:]

    # Compute Hamming distance between prefix_k and suffix_k
    distance = sum(pc != sc for pc, sc in zip(prefix_k, suffix_k))

    return distance <= delta

# Alias for backward compatibility with test
check_pattern_similarity = check_pattern_condition
