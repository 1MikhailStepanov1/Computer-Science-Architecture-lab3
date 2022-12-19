from esprima import esprima
from isa import write_code, Opcode

type2opcode = {
    'VariableDeclaration': Opcode.ALLOC,
    'input': Opcode.INPUT,
    'print': Opcode.PRINT,
    '>': Opcode.JLE,
    '>=': Opcode.JL,
    '<': Opcode.JGE,
    '<=': Opcode.JG,
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
        match i.type:
            case "VariableDeclaration":
                resCode.append({'opcode': Opcode.ALLOC, 'arg1': i.declarations[0].init.value})
            case "WhileStatement":
                translateWhileCycle(resCode, i.test, i.body)
            case _:
                break
        print(resCode)
        print("-----------------------------------")

    resCode.append({'opcode': Opcode.HALT})
    return resCode


# TODO Обращение к памяти, где лежат переменные
# TODO Количество шагов куда прыгать. Возможно не понадобится
def translateWhileCycle(resCode, condition, body):
    resCode.append({'opcode': type2opcode[condition.operator], 'arg1': condition.left.name, 'arg2': condition.right.value, 'arg3': 12})




def main():
    translate("/home/mikhail/PycharmProjects/Computer-Science-Architecture/tests/prob5_test")


if __name__ == '__main__':
    main()
