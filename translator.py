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
    'dec': Opcode.DEC
}

address_data_mem = 0x0
address_instr_mem = 0x0
var2address = {}
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
    "simpleWhileStatement": r"while[\s]*\([a-zA-z]+[\s]*(>|>=|<|<=|!=|==)[\s]*([0-9]+|[a-zA-Z]+)\)",
    "simpleIfStatement": r"if[\s]*\([a-zA-z]+[\s]*(>|>=|<|<=|!=|==)[\s]*([0-9]+|[a-zA-Z]+)\)",
    "whileWithExtraActions": r"while[\s]*\(([a-zA-z]+[\s]*(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)",
    "ifWithExtraActions": r"if[\s]*\(([a-zA-z]+[\s]*(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\/|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)",
    "assign": r"[a-zA-Z]+[\s]+=[\s]+((([a-zA-Z]+|[0-9]+)[\s]+(\%|\/|\+|\-|\*)[\s]*([a-zA-Z]+|[0-9]+))|[0-9]+|[a-zA-Z]+);",
    "alternative": r"else",
    "input": r"input\([a-zA-Z]+\);",
    "print": r"print\([a-zA-Z]+\);"
}

# TODO Переделать на нормальное if условие
banned_symbols = {'{', '}'}

res_code = []
jmp_stack = []
last_op = ''


def inc_stack():
    for x in range(0, len(jmp_stack)):
        jmp_stack[x] = jmp_stack[x] + 1


def parse(filename):
    with open(filename, encoding="utf-8") as file:
        code = file.read()
    code = code.split("\n")
    write_code("code.out", code)
    return code


def translate(filename):
    global address_instr_mem
    code = parse(filename)
    i = 0
    for i in range(i, len(code)):

        if re.fullmatch(regex_patterns.get("alloc"), code[i]) is not None:
            last_operation = 'wr'
            res_code.append(parse_alloc_instr(last_operation, code[i]))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("whileWithExtraActions"), code[i]) is not None:
            last_operation = 'while'
            jmp_stack.append({'com_addr': address_instr_mem, 'arg': 0, 'type': 'while'})
            add_load_isntr('rx14', 0)
            if re.fullmatch(regex_patterns.get("simpleWhileStatement"), code[i]) is not None:
                res_code.append(parse_condition(code[i], last_operation))
            else:
                res_code.append(parse_condition(code[i], last_operation))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("ifWithExtraActions"), code[i]) is not None:
            last_operation = 'if'
            jmp_stack.append({'com_addr': address_instr_mem, 'arg': 0, 'type': 'if'})
            add_load_isntr('rx14', 0)
            if re.fullmatch(regex_patterns.get("simpleIfStatement"), code[i]) is not None:
                res_code.append(parse_condition(code[i], last_operation))
            else:
                res_code.append(parse_condition(code[i], last_operation))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("assign"), code[i]) is not None:
            last_operation = 'wr'
            res_code.append(parse_assign_condition(last_operation, code[i]))
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("input"), code[i]) is not None:
            last_operation = 'input'
            name_of_variable = code[i].replace('input', '').replace('(', '').replace(')', '').replace(';', '')
            res_code.append({'opcode': type2opcode.get(last_operation).value, 'variable': name_of_variable})
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get("print"), code[i]) is not None:
            last_operation = 'print'
            name_of_variable = code[i].replace('print', '').replace('(', '').replace(')', '').replace(';', '')
            res_code.append({
                'opcode': type2opcode.get(last_operation).value,
                'arg1': 'rx' + str(load_var(name_of_variable))
            })
            address_instr_mem += 1

        elif re.fullmatch(regex_patterns.get('alternative'), code[i]) is not None:
            jmp_stack.append({'com_addr': address_instr_mem, 'arg1': 0, 'type': 'else'})
            add_load_isntr('rx14', 0)
            res_code.append({'opcode': type2opcode.get('jump').value})
            address_instr_mem += 1

        if code[i] == '}':
            jmp_arg = jmp_stack.pop()
            if jmp_arg['type'] == 'while':
                add_load_isntr("rx14", jmp_arg["com_addr"]-1)
                res_code.append({'opcode': type2opcode.get('jump').value})
                address_instr_mem += 1
                res_code[jmp_arg["com_addr"]].update({'arg2': address_instr_mem})
            res_code[jmp_arg["com_addr"]].update({'arg2': address_instr_mem})

    res_code.append({'opcode': Opcode.HALT.value})
    address_instr_mem += 1
    return res_code


def parse_alloc_instr(operation, row):
    row = row.split(' ')
    reg_name = "rx" + str(reg_counter)
    add_load_isntr(reg_name, int(row[len(row) - 1].replace(";", "")))
    result = {
        'opcode': type2opcode.get(operation).value,
        'arg1': 'rx2',
        'arg2': reg_name
    }
    add_var_to_map(row[1])
    change_data_reg()
    return result


def parse_condition(row, parsed_type):
    result = {
        'opcode': 0,
        'arg1': 0,
        'arg2': 0,
        'arg3': 'rx14'
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
    elif len(right) > 1:
        result.update({'arg2': parse_extra_action(right)})
    else:
        if left[0] in var2address.keys():
            reg = 'rx' + str(load_var(left[0]))
            result.update({'arg1': reg})
        elif left[0] == '0':
            result.update({'arg1': 'rx0'})
        elif check_number_in_arg(left[0]):
            add_load_isntr("rx" + str(reg_counter), left[0])
            result.update({'arg1': "rx" + str(reg_counter)})
            change_data_reg()
        if right[0] in var2address.keys():
            reg = 'rx' + str(load_var(right[0]))
            result.update({'arg2': reg})
        elif right[0] == '0':
            result.update({'arg2': 'rx0'})
        elif check_number_in_arg(right[0]):
            add_load_isntr("rx" + str(reg_counter), right[0])
            result.update({'arg2': "rx" + str(reg_counter)})
            change_data_reg()

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
            add_load_isntr('rx' + str(reg_counter), part_to_parse[0])
            change_data_reg()
            result.update({'arg1': 'rx' + str(reg_counter - 1)})
        else:
            result.update({'arg1': 'rx' + str(load_var(part_to_parse[0]))})
        if check_number_in_arg(part_to_parse[2]):
            add_load_isntr('rx' + str(reg_counter), part_to_parse[2])
            change_data_reg()
            result.update({'arg2': 'rx' + str(reg_counter - 1)})
        else:
            result.update({'arg2': 'rx' + str(load_var(part_to_parse[2]))})
        res_code.append(result)
        address_instr_mem += 1
    else:
        if part_to_parse[1] == '+':
            result.update({
                'opcode': type2opcode.get('inc').value,
                'arg1': 'rx' + str(load_var(part_to_parse[0]))
            })
            res_code.append(result)
            address_instr_mem += 1
        elif part_to_parse[1] == '-':
            result.update({
                'opcode': type2opcode.get('dec').value,
                'arg1': 'rx' + str(load_var(part_to_parse[0]))
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
        return 'rx12'
    elif part_to_parse[1] == '%':
        return 'rx13'
    else:
        return result.get('arg1')


def check_number_in_arg(row):
    try:
        float(row)
        return True
    except ValueError:
        return False


def parse_assign_condition(operation, row):
    row = row.replace(';', '').split()
    result = {'opcode': type2opcode.get(operation).value}
    if len(row) == 3:
        if check_number_in_arg(row[2]):
            add_load_isntr('rx' + str(reg_counter), row[2])
            change_data_reg()
            result.update({
                'arg1': 'rx2',
                'arg2': 'rx' + str(get_prev_data_reg())
            })
        else:
            result.update({
                'arg1': 'rx2',
                'arg2': 'rx' + str(load_var(row[2]))
            })
    else:
        result.update({
            'arg1': 'rx2',
            'arg2': parse_extra_action(row[2:])
        })
    add_load_isntr('rx2', var2address.get(row[0]))
    return result


def add_load_isntr(register, value):
    global address_instr_mem
    res_code.append({'opcode': 'ld', 'arg1': register, 'arg2': value})
    address_instr_mem += 1


def add_var_to_map(name):
    global address_data_mem
    var2address.update({name: address_data_mem})
    address_data_mem += 1


def load_var(var_name):
    add_load_isntr('rx2', var2address.get(var_name))
    reg_data = 'rx' + str(reg_counter)
    add_load_isntr(reg_data, 'rx2')
    change_data_reg()
    return get_prev_data_reg()


def main():
    opcodes = translate(sys.argv[1])
    write_code("code.out", opcodes)


if __name__ == '__main__':
    main()
