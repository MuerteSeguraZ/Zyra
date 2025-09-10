from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
for a in [1, 2, 3] {
    print(a)
}
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)