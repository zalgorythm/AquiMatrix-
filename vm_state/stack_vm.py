"""
stack_vm.py

Implements a stack-based virtual machine (VM) for executing smart contracts on AquiMatrix.
Features:
1. Stack Operations: LIFO stack for data manipulation.
2. Opcode Execution: Executes opcodes defined in opcode_library.py.
3. Gas Metering: Tracks gas usage per operation via gas_accounting.py.
4. Determinism: Uses fixed-precision arithmetic, avoids floating-point.
"""

from vm_state.opcode_library import OPCODES
from vm_state.gas_accounting import GasMeter
from vm_state.state_trie import StateTrie

class StackVM:
    def __init__(self, gas_limit, state_db):
        self.stack = []
        self.gas_meter = GasMeter(gas_limit)
        self.state_trie = StateTrie(state_db)
        self.pc = 0  # program counter
        self.bytecode = b''
        self.running = False

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def execute(self, bytecode):
        self.bytecode = bytecode
        self.pc = 0
        self.running = True

        while self.running and self.pc < len(self.bytecode):
            opcode = self.bytecode[self.pc]
            self.pc += 1

            if opcode not in OPCODES:
                raise RuntimeError(f"Invalid opcode: {opcode}")

            gas_cost = OPCODES[opcode].gas_cost
            if not self.gas_meter.consume(gas_cost):
                raise RuntimeError("Out of gas")

            OPCODES[opcode].execute(self)

        return self.state_trie.get_root()
