"""
opcode_library.py

Defines the full instruction set for the VM.
Includes:
1. Arithmetic Opcodes: ADD, SUB, MUL, DIV with gas costs.
2. Logical Opcodes: AND, OR, NOT.
3. Storage Opcodes: SSTORE, SLOAD.
4. Control Opcodes: JUMP, JUMPI, CALL.
Each opcode is a Python function with input validation and gas cost assignment.
"""

from vm_state.gas_accounting import GasMeter
from vm_state.state_trie import StateTrie

class Opcode:
    def __init__(self, code, gas_cost, execute):
        self.code = code
        self.gas_cost = gas_cost
        self.execute = execute

def op_add(vm):
    b = vm.pop()
    a = vm.pop()
    vm.push(a + b)

def op_sub(vm):
    b = vm.pop()
    a = vm.pop()
    vm.push(a - b)

def op_mul(vm):
    b = vm.pop()
    a = vm.pop()
    vm.push(a * b)

def op_div(vm):
    b = vm.pop()
    a = vm.pop()
    if b == 0:
        raise RuntimeError("Division by zero")
    vm.push(a // b)

def op_and(vm):
    b = vm.pop()
    a = vm.pop()
    vm.push(a & b)

def op_or(vm):
    b = vm.pop()
    a = vm.pop()
    vm.push(a | b)

def op_not(vm):
    a = vm.pop()
    vm.push(~a)

def op_sstore(vm):
    key = vm.pop()
    value = vm.pop()
    vm.state_trie.set(key, value)

def op_sload(vm):
    key = vm.pop()
    value = vm.state_trie.get(key)
    vm.push(value)

def op_jump(vm):
    dest = vm.pop()
    if not isinstance(dest, int) or dest < 0 or dest >= len(vm.bytecode):
        raise RuntimeError(f"Invalid jump destination: {dest}")
    vm.pc = dest

def op_jumpi(vm):
    dest = vm.pop()
    cond = vm.pop()
    if cond != 0:
        if not isinstance(dest, int) or dest < 0 or dest >= len(vm.bytecode):
            raise RuntimeError(f"Invalid jump destination: {dest}")
        vm.pc = dest

def op_call(vm):
    # Placeholder for contract call
    # TODO: Implement contract call logic
    pass

OPCODES = {
    0x01: Opcode(0x01, 3, op_add),
    0x02: Opcode(0x02, 3, op_sub),
    0x03: Opcode(0x03, 5, op_mul),
    0x04: Opcode(0x04, 5, op_div),
    0x10: Opcode(0x10, 3, op_and),
    0x11: Opcode(0x11, 3, op_or),
    0x12: Opcode(0x12, 3, op_not),
    0x20: Opcode(0x20, 200, op_sstore),
    0x21: Opcode(0x21, 50, op_sload),
    0x30: Opcode(0x30, 8, op_jump),
    0x31: Opcode(0x31, 10, op_jumpi),
    0x40: Opcode(0x40, 25, op_call),
}
