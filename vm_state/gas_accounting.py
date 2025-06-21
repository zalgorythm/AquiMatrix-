"""
gas_accounting.py

Manages resource usage during smart contract execution by tracking gas consumption and calculating fees.
Features:
1. Initializes Gas based on transaction gas limit.
2. Tracks Usage: Deducts gas for each opcode executed.
3. Fee Calculation: Multiplies gas used by gas price.
4. Enforcement: Halts execution if gas runs out, reverts state changes but retains fee.
"""

class GasMeter:
    def __init__(self, gas_limit):
        self.gas_limit = gas_limit
        self.gas_used = 0

    def consume(self, amount):
        if self.gas_used + amount > self.gas_limit:
            return False
        self.gas_used += amount
        return True

    def get_gas_used(self):
        return self.gas_used

    def calculate_fee(self, gas_price):
        return self.gas_used * gas_price
