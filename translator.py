#!/usr/bin/python3
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=consider-using-f-string

import re
import sys

from isa import write_code, Opcode

type2opcode = {
    'wr': Opcode.WR,
    'input': Opcode.INPUT,
    'print': Opcode.PRINT,
    'jump': Opcode.JUMP,
    '>': Opcode.JLE,
    '>=': Opcode.JL,
    '<': Opcode.JGE,
    '<=': Opcode.JG,
    '==': Opcode.JNE,
    '%': Opcode.DIV,
    '-': Opcode.SUB,
    '+': Opcode.ADD,
    '!=': Opcode.JE,
    '/': Opcode.DIV,
    '*': Opcode.MUL,
    'inc': Opcode.INC,
    'dec': Opcode.DEC,
    'push': Opcode.PUSH,
    'pop': Opcode.POP
}

address_data_mem = 0x0
address_instr_mem = 0x0
address2var = []
stack = 0
variables = set()
reg_counter = 3


def change_data_reg():
    global reg_counter
    reg_counter += 1
    if reg_counter > 11:
        reg_counter = 3


def get_prev_data_reg():
    if reg_counter == 3:
        return 11
    else:
        return reg_counter - 1


condition_signs = {">", ">=", "<", "<=", "==", "!="}
simple_operations = {"*", "/", "%", "+", "-"}
div_operations = {'/', '%'}

regex_patterns = {
    "alloc": r"let[\s]+[a-zA-z]+[\s]+=[\s]+([0-9]+|(\"|\').*(\"|\'));",
    "whileWithExtraActions": r"while[\s]*\(([a-zA-z]+[\s]*(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)"
                             r"|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*"
                             r"(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|"
                             r"([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)",
    "ifWithExtraActions": r"if[\s]*\(([a-zA-z]+[\s]*(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|"
                          r"[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\/|\+|\-|\*)"
                          r"[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)",
    "assign": r"[a-zA-Z]+[\s]+=[\s]+((([a-zA-Z]+|[0-9]+)[\s]+(\%|\/|\+|\-|\*)[\s]*"
              r"([a-zA-Z]+|[0-9]+))|[0-9]+|[a-zA-Z]+);",
    "alternative": r"else",
    "input": r"input\([a-zA-Z]+\);",
    "print": r"print\([a-zA-Z]+\);"
}


banned_symbols = {'{', '}'}

res_code = []
jmp_stack = []
last_op = ''


def parse(filename):
    with open(filename, encoding="utf-8") as file:
        code = file.read()
    code = code.split("\n")
    return code


def translate(filename):
    global address_instr_mem, stack
    code = parse(filename)
    for i in range(0, len(code)):
        if re.fullmatch(regex_patterns.get("alloc"), code[i]) is not None:
            parse_alloc_instr(code[i])

        elif re.fullmatch(regex_patterns.get("whileWithExtraActions"), code[i]) is not None:
            last_operation = 'while'
            jmp_stack.append({'com_addr': address_instr_mem, 'arg': 0, 'type': 'while'})
            add_load_instr('rx15', 0)
            res_code.append(parse_condition(code[i], last_operation))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("ifWithExtraActions"), code[i]) is not None:
            last_operation = 'if'
            jmp_stack.append({'com_addr': address_instr_mem, 'arg': 0, 'type': 'if'})
            add_load_instr('rx15', 0)
            res_code.append(parse_condition(code[i], last_operation))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("assign"), code[i]) is not None:
            res_code.append(parse_assign_condition(code[i]))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("input"), code[i]) is not None:
            parse_input(code[i])

        elif re.fullmatch(regex_patterns.get("print"), code[i]) is not None:
            name_of_variable = code[i].replace('print', '').replace('(', '').replace(')', '').replace(';', '')
            var_out(name_of_variable)

        elif re.fullmatch(regex_patterns.get('alternative'), code[i]) is not None:
            jmp_stack.append({'com_addr': address_instr_mem, 'arg1': 0, 'type': 'else'})
            add_load_instr('rx15', 0)
            res_code.append({'opcode': type2opcode.get('jump').value})
            address_instr_mem += 1

        elif code[i] == '}':
            jmp_arg = jmp_stack.pop()
            if jmp_arg['type'] == 'while':
                add_load_instr("rx15", jmp_arg["com_addr"])
                res_code.append({'opcode': type2opcode.get('jump').value})
                address_instr_mem += 1
                res_code[jmp_arg["com_addr"]].update({'arg2': address_instr_mem})
            elif jmp_arg['type'] == 'if' and code[i + 1] == 'else':
                res_code[jmp_arg["com_addr"]].update({'arg2': address_instr_mem + 2})
            else:
                res_code[jmp_arg["com_addr"]].update({'arg2': address_instr_mem})

    res_code.append({'opcode': Opcode.HALT.value})
    address_instr_mem += 1
    return res_code


def parse_input(row):
    global address_instr_mem
    var_name = row.replace("input(", "").replace(");", "")
    add_load_instr("rx2", get_var_addr_in_mem(var_name))
    res_code.append({'opcode': type2opcode.get('input').value})
    address_instr_mem += 1


def parse_alloc_instr(row):
    global address_data_mem
    row = row.split(' ')
    reg_name = "rx" + str(reg_counter)
    value = []
    for el in range(0, len(row)):
        if row[el] == '=':
            value = row[el + 1:]
    value[len(value) - 1] = value[len(value) - 1].replace(";", "")
    if value[0][0] == '\"' and value[len(value) - 1][len(value[len(value) - 1]) - 1] == '\"':
        if value[0] == "\"\"":
            add_load_instr('rx' + str(reg_counter), 0)
            change_data_reg()
            add_var_to_map(row[1], 'string')
            add_wr_instr('rx' + str(get_prev_data_reg()))
            return
        string_to_load = ""
        for i in value:
            string_to_load += i
            string_to_load += " "
        string_to_load = string_to_load.strip().replace("\"", "")
        if string_to_load == "":
            add_load_instr(reg_name, "rx0")
        else:
            for ch in range(0, len(string_to_load)):
                ch_in_ord = ord(string_to_load[ch])
                add_load_instr('rx' + str(reg_counter), ch_in_ord)
                change_data_reg()
                add_var_to_map(row[1], 'string')
                add_wr_instr('rx' + str(get_prev_data_reg()))

    else:
        add_var_to_map(row[1], 'int')
        add_load_instr(reg_name, int(row[len(row) - 1].replace(";", "")))
        add_wr_instr(reg_name)
        change_data_reg()


def parse_condition(row, parsed_type):
    global address_instr_mem
    result = {
        'opcode': 0,
        'arg1': 0,
        'arg2': 0,
    }
    row = row.replace('(', '').replace(')', '').split(' ')
    if parsed_type == 'if':
        row.remove('if')
    else:
        row.remove('while')
    left = []
    right = []
    index = 0
    for i in range(0, len(row)):
        if row[i] in condition_signs:
            index = i
            left = row[:i]
            right = row[i + 1:]
    if len(left) > 1:
        result.update({'arg1': parse_extra_action(left)})
    else:
        if left[0] in variables:
            reg = 'rx' + str(load_var(get_var_addr_in_mem(left[0])))
            result.update({'arg1': reg})
        elif left[0] == '0':
            result.update({'arg1': 'rx0'})
        elif check_number_in_arg(left[0]):
            add_load_instr("rx" + str(reg_counter), int(left[0]))
            result.update({'arg1': "rx" + str(reg_counter)})
            change_data_reg()

    if len(right) > 1:
        result.update({'arg2': parse_extra_action(right)})
    else:
        if right[0] in variables:
            reg = 'rx' + str(load_var(get_var_addr_in_mem(right[0])))
            result.update({'arg1': reg})
        elif right[0] == '0':
            result.update({'arg2': 'rx0'})
        elif check_number_in_arg(right[0]):
            add_load_instr("rx" + str(reg_counter), int(right[0]))
            result.update({'arg2': "rx" + str(reg_counter)})
            change_data_reg()
        elif right[0] == 'EOF':
            result.update({'arg2': 'rx0'})

    result.update({'opcode': type2opcode.get(row[index]).value})
    return result


def parse_extra_action(part_to_parse):
    global address_instr_mem
    result = {
        'opcode': 0
    }
    if part_to_parse[1] in simple_operations and part_to_parse[2] != '1':
        result.update({
            'opcode': type2opcode.get(part_to_parse[1]).value
        })
        if check_number_in_arg(part_to_parse[0]):
            add_load_instr('rx' + str(reg_counter), part_to_parse[0])
            change_data_reg()
            result.update({'arg1': 'rx' + str(reg_counter - 1)})
        else:
            result.update({'arg1': 'rx' + str(load_var(get_var_addr_in_mem(part_to_parse[0])))})
        if check_number_in_arg(part_to_parse[2]):
            add_load_instr('rx' + str(reg_counter), part_to_parse[2])
            change_data_reg()
            result.update({'arg2': 'rx' + str(reg_counter - 1)})
        else:
            result.update({'arg2': 'rx' + str(load_var(get_var_addr_in_mem(part_to_parse[2])))})
        res_code.append(result)
        address_instr_mem += 1
    else:
        if part_to_parse[1] == '+':
            result.update({
                'opcode': type2opcode.get('inc').value,
                'arg1': 'rx' + str(load_var(get_var_addr_in_mem(part_to_parse[0])))
            })
            res_code.append(result)
            address_instr_mem += 1
        elif part_to_parse[1] == '-':
            result.update({
                'opcode': type2opcode.get('dec').value,
                'arg1': 'rx' + str(load_var(get_var_addr_in_mem(part_to_parse[0])))
            })
            res_code.append(result)
            address_instr_mem += 1
        else:
            result = {
                'opcode': type2opcode.get(part_to_parse[1]).value,
                'arg1': part_to_parse[0],
                'arg2': part_to_parse[2]
            }
            res_code.append(result)
            address_instr_mem += 1
    if part_to_parse[1] == '/':
        return 'rx13'
    elif part_to_parse[1] == '%':
        return 'rx14'
    else:
        return result.get('arg1')


def parse_assign_condition(row):
    row = row.replace(';', '').split()
    result = {'opcode': type2opcode.get('wr').value}
    if len(row) == 3:
        if check_number_in_arg(row[2]):
            add_load_instr('rx' + str(reg_counter), row[2])
            change_data_reg()
            result.update({
                'arg1': 'rx' + str(get_prev_data_reg())
            })
        else:
            result.update({
                'arg1': 'rx' + str(load_var(get_var_addr_in_mem(row[2])))
            })
    else:
        result.update({
            'arg1': parse_extra_action(row[2:])
        })
    add_load_instr('rx2', get_var_addr_in_mem(row[0]))
    return result


def var_out(var_name):
    global address_instr_mem
    for var in address2var:
        if var['name'] == var_name:
            # add_load_instr("rx" + str(reg_counter), "rx2")
            reg_to_print = load_var(var['addr'])
            # res_code.append({'opcode': 'print', 'arg1': 'rx' + str(reg_counter)})
            if var['type'] == 'string':
                res_code.append({'opcode': 'print', 'arg1': 'rx' + str(reg_to_print), 'arg2': 1})
            else:
                res_code.append({'opcode': 'print', 'arg1': 'rx' + str(reg_to_print), 'arg2': 0})
            change_data_reg()
            address_instr_mem += 1


def load_var(addr):
    add_load_instr('rx2', addr)
    reg_data = 'rx' + str(reg_counter)
    add_load_instr(reg_data, 'rx2')
    change_data_reg()
    return get_prev_data_reg()


def check_number_in_arg(row):
    try:
        float(row)
        return True
    except ValueError:
        return False


def add_load_instr(register, value):
    global address_instr_mem
    res_code.append({'opcode': 'ld', 'arg1': register, 'arg2': value})
    address_instr_mem += 1


def add_wr_instr(register):
    global address_instr_mem, address_data_mem
    res_code.append({'opcode': 'wr', 'arg1': register})
    address_instr_mem += 1
    address_data_mem += 1


def add_var_to_map(name, var_type):
    global address_data_mem
    variables.add(name)
    var = {
        'addr': address_data_mem,
        'name': name,
        'type': var_type
    }
    address2var.append(var)


def add_push_instr():
    global stack, address_instr_mem
    res_code.append({'opcode': type2opcode.get('push').value, 'arg1': 'rx2'})
    address_instr_mem += 1
    stack += 1


def add_pop_instr():
    global address_instr_mem, stack
    res_code.append({'opcode': type2opcode.get('pop').value, 'arg1': 'rx2'})
    address_instr_mem += 1
    stack -= 1


def get_var_addr_in_mem(name):
    for var in address2var:
        if var['name'] == name:
            return var['addr']


def main(args):
    assert len(args) == 2, "Wrong arguments"
    source, target = args
    opcodes = translate(source)
    write_code(target, opcodes)


if __name__ == '__main__':
    main(sys.argv[1:])
