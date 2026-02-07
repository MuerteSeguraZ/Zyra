#!/usr/bin/env python3
"""
Zyra Language Interpreter
Enhanced driver with improved REPL and file execution support
"""

import sys
import os
import atexit
from pathlib import Path
from lexer import tokenize, preprocess
from parser_enhanced import Parser, ParseError
from interpreter import Interpreter, RuntimeError as InterpreterRuntimeError

# Try to import readline for better REPL experience
# Falls back gracefully if not available (e.g., on Windows)
try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

# ANSI color codes for better output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'

def setup_readline():
    """Configure readline for better REPL experience (if available)"""
    if not HAS_READLINE:
        return  # Readline not available, skip setup
    
    # History file location
    history_file = Path.home() / '.zyra_history'
    
    # Load history if it exists
    try:
        if history_file.exists():
            readline.read_history_file(history_file)
    except Exception:
        pass
    
    # Set history length
    readline.set_history_length(1000)
    
    # Save history on exit
    atexit.register(lambda: readline.write_history_file(history_file))
    
    # Enable tab completion (basic)
    readline.parse_and_bind('tab: complete')

def run_file(filename, verbose=False, debug=False):
    """Execute a source file"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        if verbose:
            print(f"{Colors.CYAN}Reading file: {filename}{Colors.RESET}")
        
        # Optionally preprocess
        # code = preprocess(code)
        
        # Tokenize
        if debug:
            print(f"{Colors.GRAY}Tokenizing...{Colors.RESET}")
        tokens = tokenize(code, track_position=True)
        
        if debug:
            print(f"{Colors.GRAY}Tokens: {tokens[:10]}...{Colors.RESET}")
        
        # Parse
        if debug:
            print(f"{Colors.GRAY}Parsing...{Colors.RESET}")
        parser = Parser(tokens)
        ast = parser.parse()
        
        if debug:
            print(f"{Colors.GRAY}AST: {ast}{Colors.RESET}")
        
        # Interpret
        if debug:
            print(f"{Colors.GRAY}Executing...{Colors.RESET}")
        interpreter = Interpreter()
        interpreter.eval(ast)
        
        if verbose:
            print(f"{Colors.GREEN}✓ Execution completed{Colors.RESET}")
        
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File '{filename}' not found{Colors.RESET}")
        sys.exit(1)
    except ParseError as e:
        print(f"{Colors.RED}Parse Error: {e}{Colors.RESET}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except InterpreterRuntimeError as e:
        print(f"{Colors.RED}Runtime Error: {e}{Colors.RESET}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Execution interrupted{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Unexpected Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def repl(verbose=False):
    """Interactive Read-Eval-Print Loop with multi-line support"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}Zyra REPL v1.0{Colors.RESET}")
    print(f"{Colors.GRAY}Type 'exit' or Ctrl+D to quit{Colors.RESET}")
    print(f"{Colors.GRAY}Type 'help' for information{Colors.RESET}")
    print(f"{Colors.GRAY}Use '\\\\' at end of line for multi-line input{Colors.RESET}")
    if not HAS_READLINE:
        print(f"{Colors.YELLOW}Note: Command history not available (readline module not found){Colors.RESET}")
    print()
    
    setup_readline()
    interpreter = Interpreter()
    
    # Track multi-line input
    multi_line_buffer = []
    in_multi_line = False
    
    while True:
        try:
            # Determine prompt
            if in_multi_line:
                prompt = f"{Colors.BLUE}... {Colors.RESET}"
            else:
                prompt = f"{Colors.GREEN}>>> {Colors.RESET}"
            
            # Read
            line = input(prompt)
            
            # Check for multi-line continuation
            if line.rstrip().endswith('\\'):
                multi_line_buffer.append(line.rstrip()[:-1])
                in_multi_line = True
                continue
            
            # Combine multi-line input
            if in_multi_line:
                multi_line_buffer.append(line)
                code = '\n'.join(multi_line_buffer)
                multi_line_buffer = []
                in_multi_line = False
            else:
                code = line
            
            # Handle special commands
            if code.strip() == "exit":
                print(f"{Colors.CYAN}Goodbye!{Colors.RESET}")
                break
            elif code.strip() == "help":
                print_help()
                continue
            elif code.strip() == "clear":
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            elif code.strip() == "vars":
                print_variables(interpreter)
                continue
            elif code.strip() == "debug-env":
                # Debug command to inspect environment structure
                if hasattr(interpreter, 'env'):
                    print(f"{Colors.GRAY}Environment type: {type(interpreter.env)}{Colors.RESET}")
                    print(f"{Colors.GRAY}Attributes: {[a for a in dir(interpreter.env) if not a.startswith('_')]}{Colors.RESET}")
                else:
                    print(f"{Colors.GRAY}No 'env' attribute found{Colors.RESET}")
                continue
            elif code.strip() == "reset":
                interpreter = Interpreter()
                print(f"{Colors.YELLOW}Interpreter state reset{Colors.RESET}")
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
            
            # Print (if result is not None and not a print statement)
            if result is not None and not code.strip().startswith(('print', 'printf')):
                # Suppress output for declarations and definitions
                should_suppress = (
                    # Check if it's a declaration/definition keyword
                    any(code.strip().startswith(kw) for kw in ['fnc', 'function', 'def', 'struct', 'enum', 'class', 'type', 'dec', 'const']) or
                    # Check if result is a function/class object
                    (hasattr(result, '__class__') and 'Function' in result.__class__.__name__) or
                    (hasattr(result, '__class__') and 'Class' in result.__class__.__name__) or
                    (hasattr(type(result), '__name__') and 'object at 0x' in str(result))
                )
                
                if not should_suppress:
                    print(f"{Colors.CYAN}{result}{Colors.RESET}")
                
        except EOFError:
            print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}")
            break
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted{Colors.RESET}")
            multi_line_buffer = []
            in_multi_line = False
            continue
        except ParseError as e:
            print(f"{Colors.RED}Parse Error: {e}{Colors.RESET}")
            multi_line_buffer = []
            in_multi_line = False
        except InterpreterRuntimeError as e:
            print(f"{Colors.RED}Runtime Error: {e}{Colors.RESET}")
            multi_line_buffer = []
            in_multi_line = False
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            if verbose:
                import traceback
                traceback.print_exc()
            multi_line_buffer = []
            in_multi_line = False

def print_variables(interpreter):
    """Print current interpreter variables"""
    try:
        # Try to get the environment object
        env = None
        if hasattr(interpreter, 'env'):
            env = interpreter.env
        elif hasattr(interpreter, 'environment'):
            env = interpreter.environment
        elif hasattr(interpreter, 'variables'):
            env = interpreter.variables
        
        if env is None:
            print(f"{Colors.GRAY}Cannot access interpreter environment{Colors.RESET}")
            return
        
        # Handle different environment types
        variables = {}
        
        # If it's a dict-like object with items()
        if hasattr(env, 'items') and callable(env.items):
            variables = dict(env.items())
        # If it's an Environment object with a vars/store attribute
        elif hasattr(env, 'vars'):
            variables = env.vars if isinstance(env.vars, dict) else {}
        elif hasattr(env, 'store'):
            variables = env.store if isinstance(env.store, dict) else {}
        elif hasattr(env, 'bindings'):
            variables = env.bindings if isinstance(env.bindings, dict) else {}
        # If it has __dict__, try that
        elif hasattr(env, '__dict__'):
            # Filter out private/magic attributes
            variables = {k: v for k, v in env.__dict__.items() if not k.startswith('_')}
        else:
            # Try to convert to dict
            try:
                variables = dict(env)
            except:
                print(f"{Colors.GRAY}Unknown environment structure{Colors.RESET}")
                return
        
        # Filter and format variables
        user_vars = {}
        builtin_funcs = set()
        
        for name, value in variables.items():
            # Handle tuple format: (value, type, is_const, is_defined)
            if isinstance(value, tuple) and len(value) >= 2:
                actual_value = value[0]
                var_type = value[1]  # The type annotation
                is_const = value[2] if len(value) > 2 else False
                
                # Skip built-in functions
                if callable(actual_value) and (
                    hasattr(actual_value, '__name__') and 
                    name in ['abs', 'int', 'float', 'str', 'len', 'max', 'min', 'sum', 'range', 'type', 'print', 'printf']
                ):
                    builtin_funcs.add(name)
                    continue
                
                user_vars[name] = (actual_value, var_type, is_const)
            else:
                # Not a tuple, store as-is with unknown type
                user_vars[name] = (value, None, False)
        
        if user_vars:
            print(f"{Colors.BOLD}User-Defined Variables:{Colors.RESET}")
            for name, (value, var_type, is_const) in sorted(user_vars.items()):
                # Determine the type to display
                if var_type:
                    type_str = f"{Colors.BLUE}{var_type}{Colors.RESET}"
                elif callable(value):
                    type_str = f"{Colors.BLUE}function{Colors.RESET}"
                elif isinstance(value, bool):
                    type_str = f"{Colors.BLUE}bool{Colors.RESET}"
                elif isinstance(value, int):
                    type_str = f"{Colors.BLUE}int{Colors.RESET}"
                elif isinstance(value, float):
                    type_str = f"{Colors.BLUE}float{Colors.RESET}"
                elif isinstance(value, str):
                    type_str = f"{Colors.BLUE}string{Colors.RESET}"
                elif isinstance(value, list):
                    type_str = f"{Colors.BLUE}array{Colors.RESET}"
                elif isinstance(value, tuple):
                    type_str = f"{Colors.BLUE}tuple{Colors.RESET}"
                elif isinstance(value, set):
                    type_str = f"{Colors.BLUE}set{Colors.RESET}"
                elif isinstance(value, dict):
                    type_str = f"{Colors.BLUE}dict{Colors.RESET}"
                else:
                    type_str = f"{Colors.BLUE}auto{Colors.RESET}"
                
                # Add const marker if needed
                if is_const:
                    type_str = f"{Colors.GRAY}const{Colors.RESET} {type_str}"
                
                # Format the value nicely
                if callable(value):
                    # Try to get function name
                    func_name = getattr(value, '__name__', None)
                    if func_name and func_name != '<lambda>':
                        val_str = f"{Colors.MAGENTA}<function {func_name}>{Colors.RESET}"
                    elif hasattr(value, 'name'):
                        val_str = f"{Colors.MAGENTA}<function {value.name}>{Colors.RESET}"
                    else:
                        val_str = f"{Colors.MAGENTA}<function>{Colors.RESET}"
                elif isinstance(value, str):
                    val_str = f'{Colors.GREEN}"{value}"{Colors.RESET}'
                elif isinstance(value, bool):
                    val_str = f"{Colors.CYAN}{str(value).lower()}{Colors.RESET}"
                elif isinstance(value, (list, tuple, set, dict)):
                    val_str = f"{Colors.CYAN}{value}{Colors.RESET}"
                else:
                    # Check if it's a custom object (like interpreter.Function)
                    obj_str = str(value)
                    if 'object at 0x' in obj_str:
                        # It's an object representation, try to make it nicer
                        class_name = type(value).__name__
                        if hasattr(value, 'name'):
                            val_str = f"{Colors.MAGENTA}<{class_name} {value.name}>{Colors.RESET}"
                        else:
                            val_str = f"{Colors.MAGENTA}<{class_name}>{Colors.RESET}"
                    else:
                        val_str = f"{Colors.CYAN}{value}{Colors.RESET}"
                
                print(f"  {type_str} {Colors.YELLOW}{name}{Colors.RESET} = {val_str}")
            
            if builtin_funcs:
                print(f"\n{Colors.GRAY}Built-in functions: {', '.join(sorted(builtin_funcs))}{Colors.RESET}")
        else:
            print(f"{Colors.GRAY}No user-defined variables{Colors.RESET}")
            if builtin_funcs:
                print(f"{Colors.GRAY}Built-in functions available: {', '.join(sorted(builtin_funcs))}{Colors.RESET}")
            
    except Exception as e:
        print(f"{Colors.RED}Error displaying variables: {e}{Colors.RESET}")
        # If verbose mode is on, show more details
        if hasattr(interpreter, 'env'):
            print(f"{Colors.GRAY}Environment type: {type(interpreter.env)}{Colors.RESET}")
            print(f"{Colors.GRAY}Available attributes: {dir(interpreter.env)}{Colors.RESET}")

def print_help():
    """Print help information"""
    help_text = f"""
{Colors.BOLD}Zyra Language Features{Colors.RESET}
{'=' * 50}

{Colors.BOLD}REPL Commands:{Colors.RESET}
  {Colors.YELLOW}help{Colors.RESET}      - Show this help message
  {Colors.YELLOW}exit{Colors.RESET}      - Exit the REPL
  {Colors.YELLOW}clear{Colors.RESET}     - Clear the screen
  {Colors.YELLOW}vars{Colors.RESET}      - Show current variables
  {Colors.YELLOW}reset{Colors.RESET}     - Reset interpreter state
  {Colors.YELLOW}\\{Colors.RESET}         - Continue on next line (multi-line input)

{Colors.BOLD}Data Types:{Colors.RESET}
  Numbers:      42, 3.14, 0xFF, 0b1010, 0o77
  Strings:      "hello", f"Hello {{name}}"
  Characters:   'a', '\\n'
  BigInt:       123456789n
  Decimal:      3.14159d
  Booleans:     true, false
  null
  Arrays:       [1, 2, 3]
  Tuples:       (1, 2, 3)
  Sets:         {{1, 2, 3}}
  Dictionaries: {{"key": "value"}}
  Ranges:       1..10, 1..=10

{Colors.BOLD}Integer Types:{Colors.RESET}
  Unsigned:     uint8, uint16, uint32, uint64, uint128, uint256
  Signed:       int8, int16, int32, int64, int128, int256
  Platform:     usize, isize, ptrdiff

{Colors.BOLD}Variables:{Colors.RESET}
  dec x = 42            // Mutable variable
  const PI = 3.14       // Constant
  dec uint32 x = 100    // Typed variable

{Colors.BOLD}Control Flow:{Colors.RESET}
  if (cond) {{ }} else {{ }}
  while (cond) {{ }}
  for (i = 0; i < 10; i++) {{ }}
  for x in range {{ }}
  switch/case
  match (pattern matching)
  break, continue, return

{Colors.BOLD}Functions:{Colors.RESET}
  fnc add(x, y) {{ return x + y }}
  fnc typed(int32 x) -> int32 {{ return x * 2 }}
  async fnc fetch() {{ ... }}
  Lambda: |x, y| x + y

{Colors.BOLD}Operators:{Colors.RESET}
  Arithmetic:   +, -, *, /, //, %, **
  Comparison:   ==, !=, <, >, <=, >=, <=>
  Logical:      and, or, xor, not, then, nand
  Bitwise:      &, |, ^, ~, <<, >>
  Augmented:    +=, -=, *=, /=, etc.

{Colors.BOLD}Data Structures:{Colors.RESET}
  struct Person {{ name: String, age: int32 }}
  enum Color {{ Red, Green, Blue }}
  type UserId = uint64

{Colors.BOLD}Error Handling:{Colors.RESET}
  try {{ }} catch (e) {{ }}
  throw "error message"

{Colors.BOLD}I/O:{Colors.RESET}
  print(expr)
  printf("format %d", value)

{Colors.BOLD}Advanced:{Colors.RESET}
  Pattern matching:      match expr {{ pattern => result }}
  Member access:         obj.field
  Array slicing:         array[1:5]
  String interpolation:  f"Value: {{x}}"
  Ternary operator:      cond ? true_val : false_val
"""
    print(help_text)

def print_usage():
    """Print command-line usage"""
    print(f"""
{Colors.BOLD}Usage:{Colors.RESET}
  {Colors.CYAN}zyra{Colors.RESET}                    Start interactive REPL
  {Colors.CYAN}zyra{Colors.RESET} {Colors.YELLOW}<file>{Colors.RESET}           Execute a Zyra source file
  {Colors.CYAN}zyra{Colors.RESET} {Colors.YELLOW}--help{Colors.RESET}          Show this help message

{Colors.BOLD}Options:{Colors.RESET}
  {Colors.YELLOW}-v, --verbose{Colors.RESET}      Show detailed execution information
  {Colors.YELLOW}-d, --debug{Colors.RESET}        Enable debug mode
  {Colors.YELLOW}-h, --help{Colors.RESET}         Show this help message
  {Colors.YELLOW}--version{Colors.RESET}          Show version information

{Colors.BOLD}Examples:{Colors.RESET}
  {Colors.CYAN}zyra{Colors.RESET}                    # Start REPL
  {Colors.CYAN}zyra{Colors.RESET} {Colors.YELLOW}script.zyra{Colors.RESET}      # Run script.zyra
  {Colors.CYAN}zyra{Colors.RESET} {Colors.YELLOW}-v script.zyra{Colors.RESET}   # Run with verbose output
  {Colors.CYAN}zyra{Colors.RESET} {Colors.YELLOW}-d script.zyra{Colors.RESET}   # Run with debug info
""")

def main():
    """Main entry point"""
    # Parse command-line arguments
    args = sys.argv[1:]
    verbose = False
    debug = False
    files = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif arg == '--version':
            print(f"{Colors.BOLD}Zyra Language Interpreter v1.0{Colors.RESET}")
            sys.exit(0)
        elif arg in ('-v', '--verbose'):
            verbose = True
        elif arg in ('-d', '--debug'):
            debug = True
            verbose = True
        elif arg.startswith('-'):
            print(f"{Colors.RED}Unknown option: {arg}{Colors.RESET}")
            print(f"Use {Colors.YELLOW}--help{Colors.RESET} for usage information")
            sys.exit(1)
        else:
            files.append(arg)
        i += 1
    
    if files:
        # File execution mode
        for filename in files:
            run_file(filename, verbose=verbose, debug=debug)
    else:
        # REPL mode
        repl(verbose=verbose)

if __name__ == "__main__":
    main()