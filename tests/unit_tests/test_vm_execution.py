"""
test_vm_execution.py

Unit tests for vm_state.stack_vm and opcode_library.
Tests:
- Stack operations: push, pop, underflow.
- Opcode execution correctness.
- Gas metering enforcement.
"""

import unittest
from vm_state.stack_vm import StackVM
from vm_state.opcode_library import OPCODES

class TestStackVM(unittest.TestCase):
    def setUp(self):
        self.vm = StackVM(gas_limit=1000, state_db={})

    def test_push_pop(self):
        self.vm.push(10)
        self.assertEqual(self.vm.pop(), 10)
        with self.assertRaises(RuntimeError):
            self.vm.pop()

    def test_opcode_add(self):
        self.vm.push(2)
        self.vm.push(3)
        OPCODES[0x01].execute(self.vm)  # ADD opcode
        self.assertEqual(self.vm.pop(), 5)

    def test_gas_metering(self):
        self.vm.gas_meter.gas_limit = 5
        self.vm.push(2)
        self.vm.push(3)
        # ADD opcode costs 3 gas, should succeed
        OPCODES[0x01].execute(self.vm)
        # Next ADD opcode should fail due to gas limit
        self.vm.push(1)
        self.vm.push(1)
        try:
            OPCODES[0x01].execute(self.vm)
            self.fail("RuntimeError not raised")
        except RuntimeError:
            pass

if __name__ == '__main__':
    unittest.main()
