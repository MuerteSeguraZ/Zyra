# Zyra Programming Language

**Zyra** is a high-level, modern programming language designed to be expressive, flexible, and easy to use. It supports imperative, functional, and structured programming paradigms with rich data structures, control flow constructs, and first-class functions.

---

## Features

* **Variables & Types**

  * Dynamic and optionally typed variables.
  * Supports `dec` for variable declaration with optional type annotation.
  * Examples:

    ```zyra
    dec x = 5          # implicit type
    dec int y = 10     # explicit type
    ```

* **Unsigned Integers**

* Zyra supports fixed-size unsigned integer types:

  * `uint8`  - 8-bit unsigned integer (0 to 255)
  * `uint16` - 16-bit unsigned integer (0 to 65,535)
  * `uint32` - 32-bit unsigned integer (0 to 4,294,967,295)
  * `uint64` - 64-bit unsigned integer (0 to 18,446,774,073,709,551,615)

* Values automatically wrap around when exceeding their maximum:

```zyra
dec uint8 a = 250
a += 10     # a is now 4 (wraps around 255)
```

* **Data Structures**

  * **Arrays**: `[1, 2, 3]`
  * **Tuples**: `(1, 2, 3)` or empty `()`
  * **Dictionaries**: `{key: value, ...}`
  * **Sets**: `{1, 2, 3}`
  * **Null / Boolean / Strings / Chars / BigInt / Decimal**

* **Control Flow**

  * **Conditionals**: `if`, `else`
  * **Loops**: `while`, `for`, `for ... in ...`
  * **Switch / Case**: `switch { case ...: ... default: ... }`
  * **Try/Catch / Throw**: `try { ... } catch (e) { ... }`
  * **Break / Continue** statements

* **Functions**

  * Defined with `fnc` keyword
  * Supports optional parameter types
  * Example:

    ```zyra
    fnc add(int a, int b) {
        return a + b
    }
    ```

* **Operators**

  * Arithmetic: `+`, `-`, `*`, `/`
  * Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`, `in`
  * Logical: `and`, `or`, `xor`, `not`, `then`, `nand`
  * Unary: `+`, `-`, `~`

* **Assignments**

  * Standard: `x = 5`
  * Augmented: `x += 1`, `y -= 2`, etc.

* **Printing**

  * `print(expr)` — prints a value
  * `printf(format, args...)` — formatted printing

* **Function Calls & Indexing**

  * Supports function calls: `foo(1, 2)`
  * Index access: `arr[0]`, `matrix[0][1]`

---

## Syntax Examples

Nearly all examples don't have the declaration. Add it via:

```zyra
dec x = <number>
```

For example:

```zyra
dec x = 10
```

### Variable Declaration

```zyra
dec x = 10
dec string name = "ZyraLang"
```

### Conditional Statements

```zyra
if (x > 5) {
    print("x is greater than 5")
} else {
    print("x is 5 or less")
}
```

```zyra
if (x != 0) {
    print("x is not zero")
} else {
    print("x is zero")
}
```

### Loops

```zyra
for (i = 0; i < 5; i += 1) {
    print(i)
}

for item in [1, 2, 3] {
    print(item)
}
```

### Functions

```zyra
fnc greet(name) {
    print("Hello, " + name)
}

greet("World")
```

### Switch Statement

```zyra
switch (x) {
    case 1:
        print("One")
    case 2:
        print("Two")
    default:
        print("Other")
}
```

### Try / Catch

```zyra
try {
    throw "Error!"
} catch (e) {
    print(e)
}
```

### Collections

```zyra
arr = [1, 2, 3]
tup = (1, 2, 3)
dict = { "name": "Zyra", "version": 1.0 }
set = {1, 2, 3}
```

### Messages

Zyra supports single-line messages (//), multi-line messages (/* */) and hashtag messages (#).

---

## Installation & Running

To run Zyra code:

```bash
zyra <file.zy>
```

---

## Notes

* Zyra emphasizes **clarity and flexibility**.
* Types are optional but encouraged for readability.
* Supports rich expressions, indexing, and nested literals.
* Designed to be **extensible**, allowing future enhancements like modules, classes, and asynchronous programming.

---

## Contributing

Contributions are welcome! Some areas for expansion:

* Adding **type checking and inference**
* Implementing **standard library functions**
* Improving **error messages and debugging tools**
* Adding **module and import support**

---
