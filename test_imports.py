#!/usr/bin/env python3
"""
Test runner for import system
Place this file in the same directory as your tokenizer_enhanced.py and ast_nodes_enhanced.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import tokenize
from ast_nodes_enhanced import *

# Simple parser with just import support for testing
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        """Peek ahead at tokens"""
        idx = self.pos + offset
        if idx < len(self.tokens):
            token = self.tokens[idx]
            return (token.type, token.value) if hasattr(token, 'type') else token
        return (None, None)

    def consume(self, expected_type=None, expected_value=None):
        """Consume a token with optional validation"""
        tok = self.peek()
        if expected_type and tok[0] != expected_type:
            raise Exception(f"Expected {expected_type}, got {tok[0]}")
        if expected_value and tok[1] != expected_value:
            raise Exception(f"Expected '{expected_value}', got '{tok[1]}'")
        self.pos += 1
        return tok

    def parse(self):
        """Parse entire program"""
        statements = []
        while self.peek()[0] is not None:
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        """Parse a single statement"""
        tok = self.peek()
        keyword = tok[1] if tok[0] == "KEYWORD" else None
        
        # Handle 'from X import Y' syntax
        if keyword == "from":
            return self.from_import_stmt()
        elif keyword == "import":
            return self.import_stmt()
        
        # Placeholder for other statements
        return Literal(None)

    def import_stmt(self):
        """Parse import statement with file path support"""
        self.consume("KEYWORD", "import")
        
        tok = self.peek()
        
        if tok[0] == "STRING":
            filepath = self.consume("STRING")[1].strip('"\'')
            
            alias = None
            if self.peek()[1] == "as":
                self.consume("KEYWORD", "as")
                alias = self.consume("ID")[1]
            
            return ImportStatement(filepath, names=None, alias=alias)
        
        elif tok[0] == "ID":
            module = self.consume("ID")[1]
            
            alias = None
            if self.peek()[1] == "as":
                self.consume("KEYWORD", "as")
                alias = self.consume("ID")[1]
            
            return ImportStatement(module + ".zy", names=None, alias=alias)
        
        else:
            raise Exception(f"Expected string or identifier after 'import', got {tok}")

    def from_import_stmt(self):
        """Parse 'from X import Y' statement"""
        self.consume("KEYWORD", "from")
        
        tok = self.peek()
        if tok[0] == "STRING":
            filepath = self.consume("STRING")[1].strip('"\'')
        elif tok[0] == "ID":
            filepath = self.consume("ID")[1] + ".zy"
        else:
            raise Exception(f"Expected string or identifier after 'from', got {tok}")
        
        self.consume("KEYWORD", "import")
        
        names = []
        while True:
            names.append(self.consume("ID")[1])
            if self.peek()[0] != "COMMA":
                break
            self.consume("COMMA")
        
        return ImportStatement(filepath, names=names, alias=None)


# Test cases
if __name__ == "__main__":
    print("Testing import syntax parsing...")
    print("="*60)
    
    test_cases = [
        ('import "math.zy"', "Import everything from math.zy"),
        ('import "utils.zy" as utils', "Import as module alias"),
        ('from "math.zy" import add, subtract', "Import specific functions"),
        ('from "utils.zy" import greet, Point', "Import function and struct"),
        ("import math", "Legacy import (auto-adds .zy)"),
    ]
    
    for test_code, description in test_cases:
        print(f"\n{description}:")
        print(f"  Code: {test_code}")
        try:
            # Debug: show tokens
            tokens = tokenize(test_code)
            print(f"  Tokens: {[(t.type, t.value) if hasattr(t, 'type') else t for t in tokens[:5]]}")
            
            parser = Parser(tokens)
            ast = parser.parse()
            stmt = ast.statements[0]
            print(f"  ✓ Module: {stmt.module}")
            print(f"  ✓ Names: {stmt.names}")
            print(f"  ✓ Alias: {stmt.alias}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Import parsing tests completed!")
    print("\nNote: To test full import functionality, you need:")
    print("  1. The complete interpreter_with_imports.py")
    print("  2. Your parser_enhanced.py with import modifications")
    print("  3. Example .zy files (math.zy, utils.zy, main.zy)")