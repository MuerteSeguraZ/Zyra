#!/usr/bin/env python3
"""
Test suite for the enhanced language
"""

from lexer import tokenize
from parser_enhanced import Parser
from interpreter import Interpreter

def test_basic_features():
    """Test basic language features"""
    print("Testing basic features...")
    
    code = """
    dec x = 42
    dec y = 10
    dec sum = x + y
    print(sum)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Basic features test passed\n")

def test_control_flow():
    """Test control flow"""
    print("Testing control flow...")
    
    code = """
    dec result = 0
    for (i = 1; i <= 5; i += 1) {
        result += i
    }
    print(result)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Control flow test passed\n")

def test_functions():
    """Test function definitions and calls"""
    print("Testing functions...")
    
    code = """
    fnc add(a, b) {
        return a + b
    }
    
    dec result = add(10, 20)
    print(result)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Functions test passed\n")

def test_typed_integers():
    """Test typed integer operations"""
    print("Testing typed integers...")
    
    code = """
    dec uint8 small = uint8(300)
    print(small)
    
    dec int32 x = int32(42)
    print(x)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Typed integers test passed\n")

def test_data_structures():
    """Test arrays, dicts, sets, tuples"""
    print("Testing data structures...")
    
    code = """
    dec arr = [1, 2, 3, 4, 5]
    print(arr[0])
    
    dec dict = {"name": "Alice", "age": 30}
    print(dict["name"])
    
    dec coords = (10, 20)
    print(coords)
    
    dec nums = {1, 2, 3}
    print(nums)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Data structures test passed\n")

def test_operators():
    """Test various operators"""
    print("Testing operators...")
    
    code = """
    // Arithmetic
    print(10 + 5)
    print(10 - 5)
    print(10 * 5)
    print(10 / 5)
    print(2 ** 3)
    
    // Comparison
    print(5 <=> 10)
    print(10 == 10)
    
    // Logical
    print(true and false)
    print(true or false)
    print(not false)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Operators test passed\n")

def test_pattern_matching():
    """Test pattern matching"""
    print("Testing pattern matching...")
    
    code = """
    fnc classify(n) {
        match n {
            0 => { print("zero") },
            1 => { print("one") },
            _ => { print("other") }
        }
    }
    
    classify(0)
    classify(1)
    classify(42)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Pattern matching test passed\n")

def test_error_handling():
    """Test try-catch"""
    print("Testing error handling...")
    
    code = """
    try {
        throw "Test error"
    } catch (e) {
        print("Caught: " + e)
    }
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Error handling test passed\n")

def test_structs():
    """Test struct definitions"""
    print("Testing structs...")
    
    code = """
    struct Point {
        x: int32,
        y: int32
    }
    
    dec p = Point { x: 10, y: 20 }
    print(p)
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Structs test passed\n")

def test_lambdas():
    """Test lambda expressions"""
    print("Testing lambdas...")
    
    code = """
    dec square = |x| x * x
    print(square(5))
    
    dec add = |a, b| a + b
    print(add(3, 7))
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Lambdas test passed\n")

def test_fibonacci():
    """Test recursive Fibonacci"""
    print("Testing Fibonacci (integration test)...")
    
    code = """
    fnc fib(n) {
        if (n <= 1) {
            return n
        }
        return fib(n - 1) + fib(n - 2)
    }
    
    print(fib(10))
    """
    
    tokens = tokenize(code, track_position=False)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(ast)
    
    print("✓ Fibonacci test passed\n")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Running Enhanced Language Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        test_basic_features,
        test_control_flow,
        test_functions,
        test_typed_integers,
        test_data_structures,
        test_operators,
        test_pattern_matching,
        test_error_handling,
        test_structs,
        test_lambdas,
        test_fibonacci,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}\n")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()