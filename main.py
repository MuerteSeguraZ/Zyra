from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
fnc test_switch(x) {
    switch (x) {
        case 1:
            print("One")
            break
        case 2:
            print("Two")
            continue
        case 3:
            print("Three")
            break
        default:
            print("Other")
    }
}

dec int a = 2
test_switch(a)
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)
