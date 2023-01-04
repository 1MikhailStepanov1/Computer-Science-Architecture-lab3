import logging
import sys
from isa import read_code


class DataMemory:
    def __init__(self, size):
        self.data = []
        self.size = size


class InstructionMemory:
    def __init__(self, size):
        self.instructions = []
        self.size = size


class ALU:
    def __init__(self):
        self.afsaf = 000


class ControlUnit:
    def __init__(self, program, data_memory, instruction_memory, alu):
        self.program = program
        self.data_memory = data_memory
        self.instruction_memory = instruction_memory
        self.alu = alu
        self._tick = 0
        self.registers = {
            'rip': 0,
            'rdx': 0,
            'rax': 0,
            'rflags': 0
        }

    def tick(self):
        self._tick += 1

    def get_current_tick(self):
        return self._tick

    def decode_instruction(self):
        instr = 0
        print("decode")
        return instr

    def execute_instruction(self, instr):
        print(instr)


def simulation(code, input_token, limit):
    data_memory = DataMemory(2048)
    instruction_memory = InstructionMemory(2048)
    alu = ALU()
    control_unit = ControlUnit(code, data_memory, instruction_memory, alu)
    instr_counter = 0

    while limit > instr_counter:
        control_unit.decode_instruction()
    return '', control_unit.get_current_tick()


def main(args):
    global code_file, input_file
    assert len(args) == 2 or len(args) == 3, "Wrong amount of arguments. Please, read instruction carefully."
    if len(args) == 2:
        prog_type, code_file = args
    elif len(args) == 3:
        prog_type, code_file, input_file = args

    if input_file is not None:
        with open(input_file, encoding="utf-8") as file:
            input_text = file.read()
            input_token = []
            for ch in input_text:
                input_token.append(ch)

    code = read_code(code_file)
    output, ticks = simulation(code, input_token, limit=1000)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
