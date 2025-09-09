from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
fnc greet(string name) {
    print("Hello, " + name)
}

greet("betatester!")

fnc add(int a, int b) {
    return a + b
}

dec int result = add(2, 3)
print(result)
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)