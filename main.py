from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec person = { "name": "Alice", "age": 30 }
print(person)
printf("Name: %s, Age: %d\n", person["name"], person["age"])
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)