from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
print(not true)    
print(not false)   
print(not (5 > 10)) 
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)