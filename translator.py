import re
import sys

from isa import write_code, Opcode

type2opcode = {
    'alloc': Opcode.ALLOC,
    'input': Opcode.INPUT,
    'print': Opcode.PRINT,
    'jump': Opcode.JUMP,
    '>': Opcode.JLE,
    '>=': Opcode.JL,
    '<': Opcode.JGE,
    '<=': Opcode.JG,
    '==': Opcode.JNE,
    '%': Opcode.DIV,
    'assign': Opcode.ASSIGN,
    '-': Opcode.SUB,
    '+': Opcode.ADD,
    '!=': Opcode.JE,
    '/': Opcode.DIV,
    '*': Opcode.MUL,
    'inc': Opcode.INC,
    'dec': Opcode.DEC
}

condition_signs = {">", ">=", "<", "<=", "==", "!="}
simple_operations = {"*", "/", "%", "+", "-"}

regex_patterns = {
    "alloc": r"let[\s]+[a-zA-z]+[\s]+=[\s]+([0-9]+|(\"|\').*(\"|\'));",
    "simpleWhileStatement": r"while[\s]*\([a-zA-z]+[\s]*(>|>=|<|<=|!=|==)[\s]*([0-9]+|[a-zA-Z]+)\)",
    "simpleIfStatement": r"if[\s]*\([a-zA-z]+[\s]*(>|>=|<|<=|!=|==)[\s]*([0-9]+|[a-zA-Z]+)\)",
    "whileWithExtraActions": r"while[\s]*\(([a-zA-z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)",
    "ifWithExtraActions": r"if[\s]*\(([a-zA-z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)",
    "assign": r"[a-zA-Z]+[\s]+=[\s]+((([a-zA-Z]+|[0-9]+)[\s]+(\%|\\|\+|\-|\*)[\s]*([a-zA-Z]+|[0-9]+))|[0-9]+|[a-zA-Z]+);",
    "alternative": r"else",
    "input": r"input\([a-zA-Z]+\);",
    "print": r"print\([a-zA-Z]+\);"
}

# TODO Переделать на нормальное if условие
banned_symbols = {'{', '}'}

res_code = []
jmp_stack = []

def inc_stack():
    for x in range(0, len(jmp_stack)):
        jmp_stack[x]['value'] = jmp_stack[x]['value'] + 1

def parse(filename):
    with open(filename, encoding="utf-8") as file:
        code = file.read()
    code = code.split("\n")
    write_code("code.out", code)
    return code


def translate(filename):
    code = parse(filename)
    for i in code:
        if re.fullmatch(regex_patterns.get("alloc"), i) is not None:
            res_code.append({'opcode': type2opcode.get('alloc').value, 'body': parse_alloc_instr(i)})

        elif re.fullmatch(regex_patterns.get("whileWithExtraActions"), i) is not None:
            if re.fullmatch(regex_patterns.get("simpleWhileStatement"), i) is not None:
                res_code.append(parse_condition(i, 'while'))
            else:
                res_code.append(parse_condition(i, 'while'))

        elif re.fullmatch(regex_patterns.get("ifWithExtraActions"), i) is not None:
            if re.fullmatch(regex_patterns.get("simpleIfStatement"), i) is not None:
                res_code.append(parse_condition(i, 'if'))
            else:
                res_code.append(parse_condition(i, 'if'))

        elif re.fullmatch(regex_patterns.get("assign"), i) is not None:

            res_code.append({'opcode': type2opcode.get('assign').value, 'body': parse_assign_condition(i)})

        elif re.fullmatch(regex_patterns.get("input"), i) is not None:
            name_of_variable = i.replace('input', '').replace('(', '').replace(')', '').replace(';', '')
            res_code.append({'opcode': type2opcode.get('input').value, 'variable': name_of_variable})

        elif re.fullmatch(regex_patterns.get("print"), i) is not None:
            name_of_variable = i.replace('print', '').replace('(', '').replace(')', '').replace(';', '')
            res_code.append({'opcode': type2opcode.get('print').value, 'variable': name_of_variable})

        elif re.fullmatch(regex_patterns.get('alternative'), i) is not None:
            res_code.append({'opcode': type2opcode.get('jump').value, "jmp_arg": 0})

        elif i == '{':
            jmp_stack.append({'opcode_index': len(res_code)-1, 'value': 1})
            # res_code.append({'opcode': '{'})

        elif i == '}':
            jmp_arg = jmp_stack.pop()
            res_code[jmp_arg['opcode_index']]['jmp_arg'] = jmp_arg['value']

        if i not in banned_symbols:
            inc_stack()

        print(res_code[len(res_code) - 1])
        print(jmp_stack)
        # print('-----------------------------------')
        #print(i)
        print('-----------------------------------')

    res_code.append({'opcode': Opcode.HALT.value})
    return res_code

# def set_jmp_arg():
#

def parse_alloc_instr(row):
    row = row.split(' ')
    result = {
        'name': row[1],
        'value': int(row[len(row) - 1].replace(";", ""))
    }
    return result


def parse_condition(row, parsed_type):
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
        parse_extra_action(left)
        left = 'result1'
    elif len(right) > 1:
        parse_extra_action(right)
        right = 'result2'
    result = {
        'opcode': type2opcode.get(row[index]).value,
        'condition': {
            'left': left,
            'right': right
        },
        'jmp_arg': 0
    }
    return result


def parse_extra_action(part_to_parse):
    result = {}
    if part_to_parse[1] in simple_operations and part_to_parse[2] != '1':
        result = {
            'opcode': type2opcode.get(part_to_parse[1]).value,
            'body': {
                'left': part_to_parse[0],
                'right': part_to_parse[2]
            }
        }
        res_code.append(result)
        print(res_code[len(res_code) - 1])
        inc_stack()
        print(jmp_stack)
        print('-----------------------------------')
    else:
        if part_to_parse[1] == '+':
            result = {
                'opcode': type2opcode.get('inc').value,
                'body': {
                    'name': part_to_parse[0]
                }
            }
            res_code.append(result)
            print(res_code[len(res_code) - 1])
            inc_stack()
            print(jmp_stack)
            print('-----------------------------------')
        elif part_to_parse[1] == '-':
            result = {
                'opcode': type2opcode.get('dec').value,
                'body': {
                    'name': part_to_parse[0]
                }
            }
            res_code.append(result)
            print(res_code[len(res_code) - 1])
            inc_stack()
            print(jmp_stack)
            print('-----------------------------------')
        else:
            result = {
                'opcode': type2opcode.get(part_to_parse[1]).value,
                'body': {
                    'left': part_to_parse[0],
                    'right': part_to_parse[2]
                }
            }
            res_code.append(result)
            print(res_code[len(res_code) - 1])
            inc_stack()
            print(jmp_stack)
            print('-----------------------------------')
    return result


def parse_assign_condition(row):
    row = row.replace(';', '').split()
    result = {}
    if len(row) == 3:
        result = {
            'left': row[0],
            'right': row[2]
        }
    else:
        parse_extra_action(row[2:])
        result = {
            'left': row[0],
            'right': 'result'
        }

    return result


def main():
    opcodes = translate(sys.argv[1])
    write_code("code.out", opcodes)


if __name__ == '__main__':
    main()
