from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

code = """
// This is a test program
fnc loop_test() {
    dec int i = 0
    while (i < 10) {
        i = i + 1
        if (i == 3) { continue }   
        if (i == 7) { break }    /* multi-line
        comment */  
        print(i)
    }
}

loop_test()
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)