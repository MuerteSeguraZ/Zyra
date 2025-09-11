from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec pi = 3.14159d
print(pi)
printf("High precision: %f\n", pi)
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)