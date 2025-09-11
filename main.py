from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec big = 12345678901234567890n
print(big)
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)