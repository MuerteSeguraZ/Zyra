from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
dec int x = 10
dec int y = 0

if (x > 5 and y == 0) {
    print("Condition passed")
}

if (x < 5 or y == 0) {
    print("Second condition passed")
}

print((x > 5) xor (y > 0))   // true
print((x > 5) then (y > 0))  // false
print((x > 5) nand (y > 0))  // true
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)