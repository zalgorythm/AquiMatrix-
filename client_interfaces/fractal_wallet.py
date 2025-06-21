"""
fractal_wallet.py

Implements a fractal wallet coordinate system for token storage integration with StateTrie.
Features:
- Fractal coordinate generation for hierarchical wallet keys.
- Helper functions to set and get token balances using fractal coordinates.
- Integration with StateTrie for storage.
- Robust input validation and error handling.
- Support for balance increment and decrement operations.
"""

from typing import Tuple, Union
from vm_state.state_trie import StateTrie

class FractalWallet:
    def __init__(self, state_trie: StateTrie):
        self.state_trie = state_trie

    def _coordinate_to_key(self, coordinate: Tuple[int, ...]) -> str:
        """
        Converts a fractal coordinate (tuple of ints) to a string key for StateTrie.
        Example: (1, 2, 3) -> "1.2.3"
        """
        if not isinstance(coordinate, tuple) or not all(isinstance(c, int) and c >= 0 for c in coordinate):
            raise ValueError("Coordinate must be a tuple of non-negative integers")
        return ".".join(str(c) for c in coordinate)

    def set_balance(self, coordinate: Tuple[int, ...], balance: Union[int, float]) -> None:
        """
        Sets the token balance at the given fractal coordinate.
        """
        if not isinstance(balance, (int, float)) or balance < 0:
            raise ValueError("Balance must be a non-negative number")
        key = self._coordinate_to_key(coordinate)
        try:
            self.state_trie.set(key, balance)
        except Exception as e:
            raise RuntimeError(f"Failed to set balance in StateTrie: {e}")

    def get_balance(self, coordinate: Tuple[int, ...]) -> Union[int, float, None]:
        """
        Gets the token balance at the given fractal coordinate.
        Returns None if not found.
        """
        key = self._coordinate_to_key(coordinate)
        try:
            balance = self.state_trie.get(key)
            if balance is None:
                return None
            if not isinstance(balance, (int, float)):
                raise ValueError("Stored balance is not a number")
            return balance
        except Exception as e:
            raise RuntimeError(f"Failed to get balance from StateTrie: {e}")

    def increment_balance(self, coordinate: Tuple[int, ...], amount: Union[int, float]) -> None:
        """
        Increments the token balance at the given fractal coordinate by the specified amount.
        """
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Amount must be a non-negative number")
        current_balance = self.get_balance(coordinate) or 0
        new_balance = current_balance + amount
        self.set_balance(coordinate, new_balance)

    def decrement_balance(self, coordinate: Tuple[int, ...], amount: Union[int, float]) -> None:
        """
        Decrements the token balance at the given fractal coordinate by the specified amount.
        """
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Amount must be a non-negative number")
        current_balance = self.get_balance(coordinate) or 0
        if amount > current_balance:
            raise ValueError("Cannot decrement balance below zero")
        new_balance = current_balance - amount
        self.set_balance(coordinate, new_balance)

# Example usage:
# state_trie = StateTrie(db)
# wallet = FractalWallet(state_trie)
# wallet.set_balance((1, 0, 2), 100)
# balance = wallet.get_balance((1, 0, 2))
# wallet.increment_balance((1, 0, 2), 50)
# wallet.decrement_balance((1, 0, 2), 30)

    def credit_mining_earnings(self, coordinate: Tuple[int, ...], amount: Union[int, float]) -> None:
        """
        Credits mining earnings to the fractal wallet at the given coordinate.
        """
        self.increment_balance(coordinate, amount)

# Usage note:
# Call credit_mining_earnings() after mining reward is finalized, e.g., in consensus or DAG entry acceptance.
# Example:
# wallet.credit_mining_earnings(miner_coordinate, reward_amount)
