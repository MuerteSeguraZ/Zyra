from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
fnc test(x) { 
    if (x > 5) { return x * 2 } 
    return x + 1 
} 
dec int result = test(10)
print(result)
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)