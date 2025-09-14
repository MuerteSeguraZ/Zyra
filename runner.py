import sys
from lexer import tokenize
from parser import Parser
from interpreter import Interpreter

def main():
    if len(sys.argv) < 2:
        print("Usage: zyra [options] <file.zyra>")
        print("Options:")
        print("  -t, --tokens   Print tokens only")
        print("  -a, --ast      Print AST only")
        print("  -d, --debug    Enable debug mode")
        sys.exit(1)

    # Parse flags
    flags = [arg for arg in sys.argv[1:] if arg.startswith("-")]
    files = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    def pretty_print_ast(node, indent=0):
        prefix = "  " * indent
        nodetype = type(node).__name__
    
        # Base: if node has no attributes, just print type
        if not hasattr(node, "__dict__") or not node.__dict__:
            print(f"{prefix}{nodetype}: {node}")
            return

        print(f"{prefix}{nodetype}:")
        for attr, value in node.__dict__.items():
            if isinstance(value, list):
                print(f"{prefix}  {attr}: [")
                for item in value:
                    pretty_print_ast(item, indent + 2)
                print(f"{prefix}  ]")
            elif hasattr(value, "__dict__"):
                print(f"{prefix}  {attr}:")
                pretty_print_ast(value, indent + 2)
            else:
                print(f"{prefix}  {attr}: {value}")

    if not files:
        print("No input file specified")
        sys.exit(1)

    filename = files[0]
    debug_mode = "-d" in flags or "--debug" in flags
    print_tokens = "-t" in flags or "--tokens" in flags
    print_ast = "-a" in flags or "--ast" in flags

    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)

    try:
        tokens = tokenize(code)
        if print_tokens:
            for tok in tokens:
                print(tok)
            return
    except Exception as e:
        print("Lexer error:", e)
        sys.exit(1)

    try:
        parser = Parser(tokens)
        ast = parser.parse()
        if print_ast:
            pretty_print_ast(ast)
            return
    except Exception as e:
        print("Parser error:", e)
        sys.exit(1)

    try:
        interpreter = Interpreter()
        if debug_mode:
            print("Running interpreter in debug mode...")
        interpreter.eval(ast)
    except Exception as e:
        print("Runtime error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
