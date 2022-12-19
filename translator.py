from esprima import esprima
from isa import write_code, Opcode

type2opcode = {
    'VariableDeclaration': Opcode.ALLOC,
    'input': Opcode.INPUT,
    'print': Opcode.PRINT,
    '>': Opcode.JLE,
    '==': Opcode.JE,
    '%': Opcode.DIV,
    'AssignmentExpression': Opcode.ASSIGN,
    '-': Opcode.SUB,
    '+': Opcode.ADD,
    '!=': Opcode.JNE
}


def parse(filename):
    with open(filename, encoding="utf-8") as file:
        code = file.read()
    code = esprima.parseScript(code)
    write_code('code.out', code)
    return code


def translate(filename):
    code = parse(filename)
    resCode = []
    for i in code.body:
        print(i)
        print("-----------------------------------")


    resCode.append({'opcode': Opcode.HALT})
    return resCode


def main():
    translate("/home/mikhail/PycharmProjects/Computer-Science-Architecture/tests/prob5_test")


if __name__ == '__main__':
    main()
