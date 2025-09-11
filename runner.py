import sys, os
from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

def main():
    if len(sys.argv) < 2:
        print("Usage: zyra <file.zyra>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)
    
    try:
        tokens = tokenize(code)
    except Exception as e:
        print("Lexer error:", e)
        sys.exit(1)
    
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except Exception as e:
        print("Parser error:", e)
        sys.exit(1)
    
    try:
        interpreter = Interpreter()
        interpreter.eval(ast)
    except Exception as e:
        print("Runtime error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()