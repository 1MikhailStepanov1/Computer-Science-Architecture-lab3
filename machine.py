import logging
import sys
from isa import Opcode, read_code


class DataPath:
    def __init__(self, data_mem_size, instr_mem_size):
        self.data_mem = [None] * data_mem_size
        self.instr_mem = [None] * instr_mem_size
        self.zero_flag = False
        self.neg_flag = False
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
            'rx12': 0,
            'rx13': 0,  # /
            'rx14': 0,  # %
            'rx15': 0  # jmp_arg
        }

    def set_flags(self, result):
        if result == 0:
            self.zero_flag = True
        if result < 0:
            self.neg_flag = True

    def drop_flags(self):
        self.zero_flag = False
        self.neg_flag = False


class ALU:
    def __init__(self, data_path):
        self.data_path = data_path

    def inc(self, left):
        res = left + 1
        self.data_path.set_flags(res)
        return res

    def dec(self, right):
        res = right - 1
        self.data_path.set_flags(res)
        return res

    def add(self, left, right):
        res = left + right
        self.data_path.set_flags(res)
        return res

    def sub(self, left, right):
        res = left - right
        self.data_path.set_flags(res)
        return res

    def mul(self, left, right):
        res = left * right
        self.data_path.set_flags(res)
        return res

    def div(self, left, right):
        return left / right, left % right


class ControlUnit:
    def __init__(self, program, data_path, alu):
        self.program = program
        self.data_path = data_path
        self.alu = alu
        self._tick = 0

    def tick(self):
        self._tick += 1

    def get_current_tick(self):
        return self._tick

    def load_program(self):
        for i in range(0, len(self.program)):
            self.data_path.instr_mem[i] = self.program[i]

    def decode_and_execute_instruction(self):
        cur_instr = self.data_path.instr_mem[self.data_path.registers.get("rx1")]
        opcode = cur_instr['opcode']
        jmp_instr = False

        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode is Opcode.LD:
            data_to_ld = 0
            if cur_instr['arg2'] == "rx2":
                data_to_ld = self.data_path.data_mem[self.data_path.registers.get("rx2")]
            else:
                data_to_ld = cur_instr['arg2']
            self.tick()

            self.data_path.registers.update({cur_instr['arg1']: data_to_ld})
            self.tick()

        if opcode is Opcode.WR:
            addr_data_mem_to_wr = self.data_path.registers.get("rx2")
            self.tick()

            self.data_path.data_mem[addr_data_mem_to_wr] = self.data_path.registers.get(cur_instr['arg1'])
            self.tick()

            self.data_path.registers.update({"rx2": addr_data_mem_to_wr + 1})
            self.tick()

        if opcode is Opcode.JUMP:
            self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
            self.tick()
            jmp_instr = True

        if opcode in {Opcode.INC, Opcode.DEC, Opcode.ADD, Opcode.SUB, Opcode.MUL}:
            res_reg = cur_instr['arg1']
            res = 0
            if opcode is Opcode.INC:
                res = self.alu.inc(self.data_path.registers.get(res_reg))
            if opcode is Opcode.DEC:
                res = self.alu.dec(self.data_path.registers.get(res_reg))
            if opcode is Opcode.ADD:
                res = self.alu.add(self.data_path.registers.get(res_reg),
                                   self.data_path.registers.get(cur_instr['arg2']))
            if opcode is Opcode.SUB:
                res = self.alu.sub(self.data_path.registers.get(res_reg),
                                   self.data_path.registers.get(cur_instr['arg2']))
            if opcode is Opcode.MUL:
                res = self.alu.mul(self.data_path.registers.get(res_reg),
                                   self.data_path.registers.get(cur_instr['arg2']))
            self.tick()

            self.data_path.registers.update({res_reg: res})
            self.tick()

        if opcode in {Opcode.JLE, Opcode.JL, Opcode.JNE, Opcode.JE, Opcode.JG, Opcode.JGE}:
            arg1 = self.data_path.registers.get(cur_instr['arg1'])
            arg2 = self.data_path.registers.get(cur_instr['arg2'])
            self.alu.sub(arg1, arg2)
            self.tick()

            if opcode is Opcode.JLE:
                if self.data_path.zero_flag or self.data_path.neg_flag:
                    self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
                    jmp_instr = True

            if opcode is Opcode.JL:
                if not self.data_path.zero_flag and self.data_path.neg_flag:
                    self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
                    jmp_instr = True

            if opcode is Opcode.JNE:
                if not self.data_path.zero_flag:
                    self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
                    jmp_instr = True

            if opcode is Opcode.JE:
                if self.data_path.zero_flag:
                    self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
                    jmp_instr = True

            if opcode is Opcode.JGE:
                if self.data_path.zero_flag or not self.data_path.neg_flag:
                    self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
                    jmp_instr = True

            if opcode is Opcode.JG:
                if not self.data_path.zero_flag and not self.data_path.neg_flag:
                    self.data_path.registers.update({"rx1": self.data_path.registers.get("rx15")})
                    jmp_instr = True

            self.tick()

            self.data_path.drop_flags()
            self.tick()

        if opcode is Opcode.DIV:
            arg1 = self.data_path.registers.get(cur_instr['arg1'])
            arg2 = self.data_path.registers.get(cur_instr['arg1'])
            res_div, res_mod = self.alu.div(arg1, arg2)
            self.tick()

            self.data_path.registers.update({"rx13": res_div})
            self.data_path.registers.update({"rx14": res_mod})
            self.tick()

        if opcode is Opcode.PRINT:
            logging.info("%s", self.data_path.registers.get(cur_instr['arg1']))

        if not jmp_instr:
            self.data_path.registers.update({"rx1": self.data_path.registers.get("rx1") + 1})
            self.tick()

    def __repr__(self):
        return "{{TICK: {}, RX1: {}, RX2: {}, RX3: {}, RX4: {}, RX5: {}, RX6: {}, RX7: {}, RX8: {}, RX9: {}, " \
               "RX10: {}, RX11: {}, RX12: {}, RX13: {}, RX14: {}, RX15: {}}}".format(
            self._tick,
            self.data_path.registers.get("rx1"),
            self.data_path.registers.get("rx2"),
            self.data_path.registers.get("rx3"),
            self.data_path.registers.get("rx4"),
            self.data_path.registers.get("rx5"),
            self.data_path.registers.get("rx6"),
            self.data_path.registers.get("rx7"),
            self.data_path.registers.get("rx8"),
            self.data_path.registers.get("rx9"),
            self.data_path.registers.get("rx10"),
            self.data_path.registers.get("rx11"),
            self.data_path.registers.get("rx12"),
            self.data_path.registers.get("rx13"),
            self.data_path.registers.get("rx14"),
            self.data_path.registers.get("rx15"),
        )


def simulation(code, input_token, instr_limit, iter_limit):
    data_path = DataPath(2048, instr_limit)
    alu = ALU(data_path)
    control_unit = ControlUnit(code, data_path, alu)
    instr_counter = 0
    try:
        control_unit.load_program()
    except IndexError:
        logging.error("Too many instructions. Please, increase size of instruction memory.")

    try:
        while True:
            assert iter_limit > instr_counter, "Too many iterations. " \
                                               "Please, increase iteration limit or correct your program."
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", control_unit)
    except StopIteration:
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

    input_token = ""
    if input_file != "":
        with open(input_file, encoding="utf-8") as file:
            input_text = file.read()
            input_token = []
            for ch in input_text:
                input_token.append(ch)

    code = read_code(code_file)
    output, ticks = simulation(code, input_token, instr_limit=2048, iter_limit=1000)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
