#!/usr/bin/env python3
"""
Enhanced Programming Language Interpreter
Main driver with REPL and file execution support
"""

import sys
from lexer import tokenize, preprocess
from parser_enhanced import Parser, ParseError
from interpreter import Interpreter, RuntimeError as InterpreterRuntimeError

def run_file(filename):
    """Execute a source file"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        # Optionally preprocess
        # code = preprocess(code)
        
        # Tokenize
        tokens = tokenize(code, track_position=True)
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.eval(ast)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except ParseError as e:
        print(f"Parse Error: {e}")
        sys.exit(1)
    except InterpreterRuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def repl():
    """Interactive Read-Eval-Print Loop"""
    print("Enhanced Language REPL v1.0")
    print("Type 'exit' or Ctrl+D to quit")
    print("Type 'help' for information\n")
    
    interpreter = Interpreter()
    
    while True:
        try:
            # Read
            code = input(">>> ")
            
            if code.strip() == "exit":
                break
            elif code.strip() == "help":
                print_help()
                continue
            elif code.strip() == "":
                continue
            
            # Tokenize
            tokens = tokenize(code, track_position=False)
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Eval
            result = interpreter.eval(ast)
            
            # Print (if result is not None)
            if result is not None and not code.strip().startswith(('print', 'printf')):
                print(result)
                
        except EOFError:
            print("\nGoodbye!")
            break
        except ParseError as e:
            print(f"Parse Error: {e}")
        except InterpreterRuntimeError as e:
            print(f"Runtime Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

def print_help():
    """Print help information"""
    print("""
Enhanced Language Features:
===========================

Data Types:
  - Numbers: 42, 3.14, 0xFF, 0b1010, 0o77
  - Strings: "hello", f"Hello {name}"
  - Characters: 'a', '\\n'
  - BigInt: 123456789n
  - Decimal: 3.14159d
  - Booleans: true, false
  - null
  - Arrays: [1, 2, 3]
  - Tuples: (1, 2, 3)
  - Sets: {1, 2, 3}
  - Dictionaries: {"key": "value"}
  - Ranges: 1..10, 1..=10

Integer Types:
  - Unsigned: uint8, uint16, uint32, uint64, uint128, uint256
  - Signed: int8, int16, int32, int64, int128, int256
  - Platform: usize, isize, ptrdiff

Variables:
  - dec x = 42          // Mutable variable
  - const PI = 3.14     // Constant
  - dec uint32 x = 100  // Typed variable

Control Flow:
  - if (cond) { } else { }
  - while (cond) { }
  - for (i = 0; i < 10; i++) { }
  - for x in range { }
  - switch/case
  - match (pattern matching)
  - break, continue, return

Functions:
  - fnc add(x, y) { return x + y }
  - fnc typed(int32 x) -> int32 { return x * 2 }
  - async fnc fetch() { ... }
  - Lambda: |x, y| x + y

Operators:
  - Arithmetic: +, -, *, /, //, %, **
  - Comparison: ==, !=, <, >, <=, >=, <=>
  - Logical: and, or, xor, not, then, nand
  - Bitwise: &, |, ^, ~, <<, >>
  - Augmented: +=, -=, *=, /=, etc.

Data Structures:
  - struct Person { name: String, age: int32 }
  - enum Color { Red, Green, Blue }
  - type UserId = uint64

Error Handling:
  - try { } catch (e) { }
  - throw "error message"

I/O:
  - print(expr)
  - printf("format %d", value)

Advanced:
  - Pattern matching with match
  - Member access: obj.field
  - Array slicing: array[1:5]
  - String interpolation: f"Value: {x}"
  - Ternary: cond ? true_val : false_val
""")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # File execution mode
        run_file(sys.argv[1])
    else:
        # REPL mode
        repl()

if __name__ == "__main__":
    main()