from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec letter = 'a'
print(letter)

dec newline = '\\n'
printf("This is a line%cThis is another\\n", newline)
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)