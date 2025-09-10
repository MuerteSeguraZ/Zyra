from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec a = null
print(a)          # prints: None
printf("Value: %s\n", a)  # prints: Value: None
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)