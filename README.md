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

* **Unsigned & Signed Integer Types**

* Zyra supports both fixed-size unsigned and signed integers, as well as platform-sized integers:

  * Unsigned integers:

  * `uint8`  - 8-bit unsigned integer (0 to 255)
  * `uint16` - 16-bit unsigned integer (0 to 65,535)
  * `uint32` - 32-bit unsigned integer (0 to 4,294,967,295)
  * `uint64` - 64-bit unsigned integer (0 to 18,446,774,073,709,551,615)
  * `uint128` - 128-bit unsigned integer (0 to 340,282,366,920,938,463,463,374,607,431,768,211,455)
  * `usize`  - pointer-sized signed integer (wraps using two's complement, 64-bit by default)

  * Signed integers:
  * `int8`   - 8-bit signed integer (-128 to 127)
  * `int16`  - 16-bit signed integer (-32,768 to 32,767)
  * `int32`  - 32-bit signed integer (-2,147,483,648 to 2,147,483,647)
  * `int64`  - 64-bit signed integer (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807)
  * `int128` - 128-bit signed integer (-170,141,183,460,469,231,731,687,303,715,884,105,728 to 170,141,183,460,469,231,731,687,303,715,884,105,727)
  * `isize`  - pointer-sized signed integer (wraps using two’s complement, 64-bit by default)
  * `ptrdiff`- signed pointer-sized integer for storing pointer differences (wraps using two's complement, 64-bit by default)

* Values automatically wrap around when exceeding their maximum for unsigned integers, and signed integers wrap according to two’s complement rules:

```zyra
dec uint8 a = 250
a += 10     # a is now 4 (wraps around 255)

dec int8 b = 120
b += 10
print(b) # -126

dec isize c = 9223372036854775807
c += 1
print(c)   # -9223372036854775808

dec usize d =  18446744073709551615
d += 1
print(d) # 0

dec int128 a = 170141183460469231731687303715884105727
a += 1
print(a)   # -170141183460469231731687303715884105728

dec uint128 b = 340282366920938463463374607431768211455
b += 1
print(b)   
```

```zyra
# Test ptrdiff

# declare some ptrdiff variables
dec ptrdiff pd1 = ptrdiff(100)
dec ptrdiff pd2 = ptrdiff(40)

# pointer difference arithmetic
dec ptrdiff diff = pd1 - pd2
print(diff)          # expected: 60

# negative difference
dec ptrdiff neg_diff = pd2 - pd1
print(neg_diff)      # expected: -60

# wrapping test (simulate overflow)
dec ptrdiff big = ptrdiff(9223372036854775807)  # max int64
dec ptrdiff wrapped = big + ptrdiff(10)
print(wrapped)       # expected: -9223372036854775799

# mixed arithmetic with integers
dec int64 x = 50
dec ptrdiff sum = diff + ptrdiff(x)
print(sum)           # expected: 110
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
  * Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`, `<=>`, `in`
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
