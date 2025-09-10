from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
try {
    throw "Something went wrong"
} catch (e) {
    print(e)
}
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)