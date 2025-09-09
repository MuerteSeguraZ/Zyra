from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec int x = 0

while (x < 5) {
    if (x == 2) {
        print("x is two")
    } else {
        print("x is " + x)
    }
    x = x + 1
}
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)

print("Environment:", interpreter.env.vars)
