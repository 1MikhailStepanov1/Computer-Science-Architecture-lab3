import logging
import sys
from isa import read_code


class DataMemory:
    def __init__(self, size):
        self.data = [None] * size


class InstructionMemory:
    def __init__(self, size):
        self.instructions = [None] * size


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
            'rx0': 0x0,  # Регистр, постоянно хранящий 0
            'rx1': 0x0,  # Регистр текущей инструкции
            'rx2': 0x0,  # Регистр адресации в DataMemory
            'rx3': 0,  # Регистры данных
            'rx4': 0,
            'rx5': 0,
            'rx6': 0,
            'rx7': 0,
            'rx8': 0,
            'rx9': 0,
            'rx10': 0,
            'rx11': 0,
            'rx12': 0,  # /
            'rx13': 0,  # %
            'rx14': 0,  # jmp_arg
            'rflags': 0
        }

    def tick(self):
        self._tick += 1

    def get_current_tick(self):
        return self._tick

    def decode_instruction(self):
        print("Privet")

    def execute_instruction(self, dec_instr):
        print(dec_instr)


def simulation(code, input_token, limit):
    data_memory = DataMemory(2048)
    instruction_memory = InstructionMemory(limit)
    alu = ALU()
    control_unit = ControlUnit(code, data_memory, instruction_memory, alu)
    instr_counter = 0
    try:
        for instr in code:
            dec_instr = control_unit.decode_instruction()

    except IndexError:
        logging.error("Too many instructions. Please, increase size of instruction memory.")
    except StopIteration():
        pass
    return '', control_unit.get_current_tick()


def main(args):
    code_file = ""
    input_file = ""
    assert len(args) == 2 or len(args) == 3, "Wrong amount of arguments. Please, read instruction carefully."
    if len(args) == 2:
        prog_type, code_file = args
    elif len(args) == 3:
        prog_type, code_file, input_file = args

    if input_file is not "":
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
