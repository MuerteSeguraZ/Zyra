# Enhanced Programming Language

A modern, feature-rich programming language with strong type support, pattern matching, unions, and Vale-inspired design principles.

## Features

### Type System
- **Basic Types**: integers, floats, strings, characters, booleans, null
- **Integer Types**: 
  - Unsigned: `uint8`, `uint16`, `uint32`, `uint64`, `uint128`, `uint256`
  - Signed: `int8`, `int16`, `int32`, `int64`, `int128`, `int256`
  - Platform-dependent: `usize`, `isize`, `ptrdiff`
- **Special Literals**:
  - BigInt: `123456789n`
  - Decimal: `3.14159d`
  - Hex: `0xFF`, `0x1A.4F`
  - Binary: `0b1010`
  - Octal: `0o77`
- **Collections**: Arrays, Tuples, Sets, Dictionaries, Ranges

### Variables
```javascript
dec x = 42                    // Type-inferred mutable variable
dec uint32 count = 0          // Typed variable
const PI = 3.14159d           // Constant
dec mut value = 100           // Explicitly mutable
```

### Control Flow
```javascript
// If-elif-else
if (x > 0) {
    print("positive")
} elif (x < 0) {
    print("negative")
} else {
    print("zero")
}

// For loops
for (i = 0; i < 10; i++) { }
for x in 1..10 { }            // Range iteration
for item in array { }         // Collection iteration

// While loops
while (condition) { }

// Switch
switch (value) {
    case 1: print("one") break
    case 2: print("two") break
    default: print("other")
}

// Pattern matching
match value {
    0 => { print("zero") },
    1..=10 => { print("small") },
    n if n > 100 => { print("large") },
    _ => { print("other") }
}
```

### Functions
```javascript
// Basic function
fnc greet(name) {
    print("Hello, " + name)
}

// Typed function with return type
fnc add(int32 a, int32 b) -> int32 {
    return a + b
}

// Default parameters
fnc power(base, exp = 2) {
    return base ** exp
}

// Async functions
async fnc fetchData() {
    dec data = await getData()
    return data
}

// Lambda expressions
dec square = |x| x * x
dec add = |a, b| a + b
```

### Data Structures

#### Structs
```javascript
// Basic struct
struct Point {
    x: int32,
    y: int32
}

dec p = Point { x: 10, y: 20 }
print(p.x)  // 10

// Typedef struct with default values
typedef struct Color {
    r: uint8 = 0,
    g: uint8 = 0,
    b: uint8 = 0,
    a: uint8 = 255
}

dec red = Color { r: 255 }          // Other fields use defaults
dec green = Color { g: 255, a: 128 }

// Using keyword names as fields (e.g., 'type', 'static', 'const')
typedef struct Metadata {
    type: String,      // 'type' is a keyword but can be used as field name
    static: bool,
    const: bool
}

dec meta = Metadata { 
    type: "function", 
    static: true, 
    const: false 
}
print(meta.type)  // Access keyword-named fields normally
```

#### Unions
```javascript
// Basic union - only one field active at a time
union Color {
    r: uint8,
    g: uint8,
    b: uint8
}

dec red = Color { r: 255 }
print(red.r)  // 255
// print(red.g)  // ERROR: field 'g' is not active

// Typedef union
typedef union Value {
    i: int32,
    f: float32,
    s: String
}

dec int_val = Value { i: 42 }
print(int_val.i)  // 42

// Struct with anonymous union
typedef struct Packet {
    type: uint8,
    union {
        data_int: int32,
        data_float: float32
    }
}

dec packet = Packet { type: 1, data_int: 100 }
print(packet.type)      // 1
print(packet.data_int)  // 100
// print(packet.data_float)  // ERROR: not the active union field
```

#### Enums
```javascript
enum Color {
    Red,
    Green,
    Blue,
    RGB(int32, int32, int32)
}

// Type aliases
type UserId = uint64
```

### Operators

#### Arithmetic
- `+`, `-`, `*`, `/`, `//` (floor division), `%` (modulo), `**` (power)

#### Comparison
- `==`, `!=`, `<`, `>`, `<=`, `>=`
- `<=>` (spaceship/three-way comparison)
- `===`, `!==` (identity comparison)

#### Logical
- `and` / `&&`, `or` / `||`, `not` / `!`
- `xor` (exclusive or)
- `then` (logical implication)
- `nand` (not and)

#### Bitwise
- `&` (and), `|` (or), `^` (xor), `~` (not)
- `<<` (left shift), `>>` (right shift)

#### Augmented Assignment
- `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`
- `&=`, `|=`, `^=`, `<<=`, `>>=`

#### Other
- `? :` (ternary)
- `++`, `--` (increment/decrement)
- `in` (membership)
- `..`, `..=` (ranges)

### Collections

```javascript
// Arrays
dec arr = [1, 2, 3, 4, 5]
print(arr[0])

// Dictionaries
dec person = {
    "name": "Alice",
    "age": 30
}
print(person["name"])

// Sets
dec numbers = {1, 2, 3}
dec evens = {2, 4, 6}
dec union = numbers + evens
dec intersection = numbers * evens

// Tuples
dec coords = (10, 20, 30)

// Ranges
dec range1 = 1..10      // 1 to 9
dec range2 = 1..=10     // 1 to 10 (inclusive)
```

### Error Handling
```javascript
// Try-catch with multiple catch clauses
try {
    dec result = divide(10, 0)
} catch (DivisionError e) {
    print("Division error: " + e)
} catch (e) {
    print("Other error: " + e)
} finally {
    print("Cleanup")
}

// Throw exceptions
throw "Something went wrong!"
```

### Pattern Matching
```javascript
match value {
    // Literal patterns
    0 => { print("zero") },
    42 => { print("answer") },
    
    // Range patterns
    1..=10 => { print("small") },
    
    // Guard clauses
    n if n < 0 => { print("negative") },
    
    // Tuple patterns
    (0, 0) => { print("origin") },
    (x, y) => { print("point") },
    
    // Wildcard
    _ => { print("default") }
}
```

### I/O
```javascript
// Print with newline
print(value)

// Printf-style formatting
printf("Name: %s, Age: %d\n", name, age)

// String interpolation (when available)
dec name = "Alice"
// f"Hello, {name}!"
```

### Advanced Features

#### Member Access
```javascript
struct Person {
    name: String,
    age: int32
}

dec p = Person { name: "Bob", age: 25 }
print(p.name)
p.age = 26
```

#### Array Slicing
```javascript
dec arr = [1, 2, 3, 4, 5]
dec slice = arr[1:4]      // [2, 3, 4]
// dec every_other = arr[::2] // [1, 3, 5]
```

#### Method Chaining
```javascript
// obj.method1().method2().method3()
```

#### Keywords as Identifiers
The language supports using keywords as field names, variable names, and member names in appropriate contexts:

```javascript
// Keywords as struct field names
typedef struct Config {
    type: String,
    const: bool,
    static: bool,
    import: String
}

dec config = Config { 
    type: "module", 
    const: true, 
    static: false,
    import: "std"
}

// Access keyword-named fields
print(config.type)
print(config.const)
```

## Installation & Usage

### Running Programs

```bash
# Execute a file
python3 main.py program.zy

# Interactive REPL
python3 main.py
```

### REPL Commands
- `help` - Show help information
- `exit` - Exit the REPL
- Ctrl+D - Exit the REPL

## File Structure

```
tokenizer.py              - Lexical analysis
ast_nodes_enhanced.py     - AST node definitions
parser_enhanced.py        - Syntax analysis
interpreter_enhanced.py   - Runtime execution
main.py                   - Main entry point & REPL
examples.zy               - Example programs
```

## Language Philosophy

This language is designed with the following principles:

1. **Safety**: Strong typing with overflow protection for integer types
2. **Memory Safety**: Unions enforce single-field access to prevent undefined behavior
3. **Expressiveness**: Modern syntax with pattern matching and functional features
4. **Performance**: Efficient integer operations with explicit bit sizes
5. **Clarity**: Clear, readable syntax inspired by modern languages
6. **Practicality**: Built-in support for common programming patterns
7. **Flexibility**: Keywords can be used as identifiers in appropriate contexts

## Examples

### Hello World
```javascript
print("Hello, World!")
```

### FizzBuzz
```javascript
for i in 1..=100 {
    if (i % 15 == 0) {
        print("FizzBuzz")
    } elif (i % 3 == 0) {
        print("Fizz")
    } elif (i % 5 == 0) {
        print("Buzz")
    } else {
        print(i)
    }
}
```

### Factorial
```javascript
fnc factorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}

print(factorial(5))  // 120
```

### Struct with Default Values
```javascript
typedef struct Rectangle {
    width: int32,
    height: int32,
    color: String = "black",
    filled: bool = false
}

fnc area(rect) {
    return rect.width * rect.height
}

dec r = Rectangle { width: 10, height: 20 }
print(area(r))      // 200
print(r.color)      // "black" (default value)
print(r.filled)     // false (default value)
```

### Union Example (Tagged Union Pattern)
```javascript
typedef union Result {
    ok: int32,
    error: String
}

fnc divide(a, b) {
    if (b == 0) {
        return Result { error: "Division by zero" }
    }
    return Result { ok: a / b }
}

dec result = divide(10, 2)
// Check which field is active before accessing
```

### Complex Data Structure
```javascript
typedef struct Point3D {
    x: int32,
    y: int32,
    z: int32
}

fnc distance_squared(p1, p2) {
    dec dx = p2.x - p1.x
    dec dy = p2.y - p1.y
    dec dz = p2.z - p1.z
    return dx*dx + dy*dy + dz*dz
}

dec origin = Point3D { x: 0, y: 0, z: 0 }
dec point = Point3D { x: 3, y: 4, z: 0 }
print(distance_squared(origin, point))  // 25
```

## Key Language Features

### Union Safety
Unions enforce that only one field can be active at a time, preventing undefined behavior:

```javascript
union Status {
    success: int32,
    error: String
}

dec result = Status { success: 42 }
print(result.success)  // ✓ OK - active field
// print(result.error)  // ✗ ERROR - inactive field
```

### Anonymous Unions in Structs
Combine regular fields with union fields for efficient memory usage:

```javascript
typedef struct NetworkPacket {
    protocol: uint8,
    union {
        tcp_data: int32,
        udp_data: float32
    }
}

dec packet = NetworkPacket { protocol: 6, tcp_data: 1234 }
print(packet.protocol)   // 6
print(packet.tcp_data)   // 1234
```

### Type Wrapping
Integer types automatically wrap on overflow:

```javascript
dec uint8 x = uint8(300)  // Wraps to 44
dec int8 y = int8(-200)   // Wraps with two's complement
```

## Future Enhancements

- [X] Module system with imports
- [ ] Traits and implementations
- [ ] Generic types
- [ ] Enum variant destructuring in match
- [ ] Standard library
- [ ] Package manager
- [ ] Better error messages with stack traces and line numbers
- [ ] Debugger support
- [ ] IDE integration
- [ ] Optimizing compiler
- [ ] Concurrency primitives
- [ ] Memory management options
- [ ] Full string interpolation support
- [ ] Array comprehensions

## Comparison with Vale

While inspired by Vale's philosophy, this language focuses on:
- Simpler initial implementation
- Python-based runtime for easy experimentation
- Gradual type system
- Pattern matching as a first-class feature
- Flexible integer types for system programming
- C-style unions with safety enforcement

## Recent Updates

### v0.3.0
- ✅ Added import support
- ✅ Import supports relative paths

## Contributing

This is an experimental language designed for learning and exploration. Contributions, suggestions, and feedback are welcome!

## License

MIT License - Feel free to use, modify, and distribute.

---

**Note**: This language is under active development. Features and syntax may change. See `examples.zy` for comprehensive usage examples.