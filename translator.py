import re
import sys

from isa import write_code, Opcode

type2opcode = {
    'alloc': Opcode.ALLOC,
    'input': Opcode.INPUT,
    'print': Opcode.PRINT,
    '>': Opcode.JLE,
    '>=': Opcode.JL,
    '<': Opcode.JGE,
    '<=': Opcode.JG,
    '==': Opcode.JE,
    '%': Opcode.DIV,
    'assign': Opcode.ASSIGN,
    '-': Opcode.SUB,
    '+': Opcode.ADD,
    '!=': Opcode.JNE
}

condition_signs = {">", ">=", "<", "<=", "==", "!="}

regex_patterns = {
    "alloc": 'let[\s]+[a-zA-z]+[\s]+=[\s]+([0-9]+|(\"|\').*(\"|\'));',
    "simpleWhileStatement": "while[\s]*\([a-zA-z]+[\s]*(>|>=|<|<=|!=|==)[\s]*([0-9]+|[a-zA-Z]+)\)",
    "simpleIfStatement": "if[\s]*\([a-zA-z]+[\s]*(>|>=|<|<=|!=|==)[\s]*([0-9]+|[a-zA-Z]+)\)",
    "whileWithExtraActions": 'while[\s]*\(([a-zA-z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)',
    "ifWithExtraActions": 'if[\s]*\(([a-zA-z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-z]+)|[a-zA-z]+[\s]*)[\s]+(>|>=|<|<=|!=|==)[\s]+([0-9]+|[a-zA-Z]+|([a-zA-Z]+[\s]*(\%|\\|\+|\-|\*)[\s]*([0-9]+|[a-zA-Z]+))|([a-zA-Z]+(\%|\/|\+|\-|\*)([0-9]+|[a-zA-Z]+)))\)',
    "assign": '[a-zA-Z]+[\s]*=[\s]*([0-9]+|([a-zA-Z]+|[0-9]+)[\s]*(\%|\\|\+|\-|\*)[\s]*([a-zA-Z]+|[0-9]+));',
    "alternative": 'else',
    "input": 'input\([a-zA-Z]+\);',
    "print": 'print\([a-zA-Z]+\);'
}

# TODO Переделать на нормальное if условие
banned_symbols = {'{', '}'}


def parse(filename):
    with open(filename, encoding="utf-8") as file:
        code = file.read()
    code = code.split("\n")
    write_code("code.out", code)
    return code


def translate(filename):
    code = parse(filename)
    res_code = []
    jmp_stack = []
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
            res_code.append({'opcode': type2opcode.get('assign')})

        elif re.fullmatch(regex_patterns.get("input"), i) is not None:
            res_code.append({'opcode': 'input'})

        elif re.fullmatch(regex_patterns.get("print"), i) is not None:
            res_code.append({'opcode': 'print'})

        elif re.fullmatch(regex_patterns.get('alternative'), i) is not None:
            res_code.append({'opcode': 'alternative'})

        elif i == '{':
            jmp_stack.append(1)
            res_code.append({'opcode': '{'})

        elif i == '}':
            jmp_arg = jmp_stack.pop()
            res_code.append({'opcode': '}'})

        if i not in banned_symbols:
            for x in range(0, len(jmp_stack)):
                jmp_stack[x] = jmp_stack[x] + 1

        print(jmp_stack)
        print('-----------------------------------')
        print(i)
        print(res_code[len(res_code) - 1])
        print('-----------------------------------')

    res_code.append({'opcode': Opcode.HALT})
    return res_code


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
    result = {
        'opcode': type2opcode.get(row[index]).value,
        'condition': {
            'left': left,
            'right': right,
            'jmp_arg': 0
        }
    }
    return result


def main():
    opcodes = translate(sys.argv[1])
    write_code("code.out", opcodes)


if __name__ == '__main__':
    main()
