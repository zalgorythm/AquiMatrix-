"""
state_trie.py

Manages the Merkle Patricia Trie (MPT) storing the state of all smart contracts.
Features:
1. State Storage: Maps contract addresses and storage keys to values.
2. State Updates: Applies changes from contract execution.
3. Root Computation: Calculates state root hash after each update.
4. Efficiency: Uses path compression and branching.
5. Verification: Allows nodes to verify state integrity.
Integrates with database_access.py for persistence and consensus_engine components.
"""

import hashlib

class TrieNode:
    def __init__(self):
        self.children = {}
        self.value = None

class StateTrie:
    def __init__(self, db):
        self.db = db
        self.root = TrieNode()

    def get(self, key):
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.value

    def set(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.value = value
        self.persist()

    def persist(self):
        # Placeholder for persistence logic with database_access.py
        pass

    def compute_root(self):
        """
        Compute the root hash of the trie.
        """
        def hash_node(node):
            if node is None:
                return b''
            if not node.children and node.value is not None:
                return hashlib.sha256(str(node.value).encode('utf-8')).digest()
            combined = b''.join([hash_node(child) for child in node.children.values()])
            if node.value is not None:
                combined += hashlib.sha256(str(node.value).encode('utf-8')).digest()
            return hashlib.sha256(combined).digest()
        return hash_node(self.root)

    def get_root(self):
        return self.compute_root()
