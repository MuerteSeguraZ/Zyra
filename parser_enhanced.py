from ast_nodes_enhanced import *

class ParseError(Exception):
    """Custom parse error with position info"""
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        if token and hasattr(token, 'line'):
            super().__init__(f"{message} at line {token.line}, column {token.column}")
        else:
            super().__init__(message)

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
            raise ParseError(f"Expected {expected_type}, got {tok[0]}", 
                           self.tokens[self.pos] if self.pos < len(self.tokens) else None)
        if expected_value and tok[1] != expected_value:
            raise ParseError(f"Expected '{expected_value}', got '{tok[1]}'",
                           self.tokens[self.pos] if self.pos < len(self.tokens) else None)
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
        
        # Keywords
        if keyword == "dec":
            return self.var_decl()
        elif keyword == "const":
            return self.const_decl()
        elif keyword == "if":
            return self.if_stmt()
        elif keyword == "while":
            return self.while_stmt()
        elif keyword == "for":
            return self.for_stmt()
        elif keyword == "print":
            return self.print_stmt()
        elif keyword == "printf":
            return self.printf_stmt()
        elif keyword == "fnc":
            return self.function_def()
        elif keyword == "return":
            self.consume("KEYWORD", "return")
            expr = self.expr() if self.peek()[0] not in ("SEMICOL", "RBRACE", None) else None
            return ReturnStatement(expr)
        elif keyword == "break":
            self.consume("KEYWORD", "break")
            value = self.expr() if self.peek()[0] not in ("SEMICOL", "RBRACE", None) else None
            return BreakStatement(value)
        elif keyword == "continue":
            self.consume("KEYWORD", "continue")
            return ContinueStatement()
        elif keyword == "switch":
            return self.switch_stmt()
        elif keyword == "match":
            return self.match_stmt()
        elif keyword == "try":
            return self.try_catch_stmt()
        elif keyword == "throw":
            self.consume("KEYWORD", "throw")
            expr = self.expr()
            return ThrowStatement(expr)
        elif keyword == "struct":
            return self.struct_def()
        elif keyword == "enum":
            return self.enum_def()
        elif keyword == "type":
            return self.type_alias()
        elif keyword == "import":
            return self.import_stmt()
        elif keyword == "yield":
            self.consume("KEYWORD", "yield")
            expr = self.expr()
            return YieldStatement(expr)
        else:
            return self.assignment_or_expr()

    def block(self):
        """Parse a block of statements"""
        self.consume("LBRACE")
        stmts = []
        while self.peek()[0] != "RBRACE":
            if self.peek()[0] is None:
                raise ParseError("Unexpected end of input, expected '}'")
            stmts.append(self.statement())
        self.consume("RBRACE")
        return stmts

    def var_decl(self):
        """Parse variable declaration"""
        self.consume("KEYWORD", "dec")
        
        # Check for mutability modifiers
        is_mut = True
        if self.peek()[1] == "mut":
            self.consume()
            is_mut = True
        
        first_id = self.consume("ID")[1]

        # Typed declaration: dec uint8 x = expr
        if self.peek()[0] == "ID":
            var_type = first_id
            name = self.consume("ID")[1]
            self.consume("OP", "=")
            value = self.expr()
            return VarDecl(var_type, name, value, is_mut=is_mut)
        # Untyped declaration: dec x = expr
        else:
            name = first_id
            self.consume("OP", "=")
            value = self.expr()
            return VarDecl(None, name, value, is_mut=is_mut)

    def const_decl(self):
        """Parse constant declaration"""
        self.consume("KEYWORD", "const")
        name = self.consume("ID")[1]
        
        var_type = None
        if self.peek()[0] == "COLON":
            self.consume("COLON")
            var_type = self.consume("ID")[1]
        
        self.consume("OP", "=")
        value = self.expr()
        return VarDecl(var_type, name, value, is_const=True, is_mut=False)

    def assignment_or_expr(self):
        """Parse assignment or expression statement"""
        tok = self.peek()

        if tok[0] == "ID":
            # Look ahead to determine if it's an assignment
            if self.peek(1)[1] in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "**="]:
                name = self.consume("ID")[1]
                op = self.consume()[1]
                value = self.expr()
                
                if op == "=":
                    return Assignment(name, value)
                else:
                    return AugmentedAssignment(name, op, value)
            # Check for member access assignment: obj.field = value
            elif self.peek(1)[0] == "DOT":
                expr = self.expr()
                if self.peek()[1] == "=":
                    self.consume("OP", "=")
                    value = self.expr()
                    return Assignment(expr, value)
                return expr
        
        # Otherwise just an expression
        return self.expr()

    def if_stmt(self):
        """Parse if statement with elif support"""
        # Handle both 'if' and 'elif'
        tok = self.peek()
        if tok[1] == "elif":
            self.consume("KEYWORD", "elif")
        else:
            self.consume("KEYWORD", "if")
        
        self.consume("LPAREN")
        condition = self.expr()
        self.consume("RPAREN")
        then_body = self.block()
        
        else_body = None
        if self.peek()[1] == "elif":
            # Recursively parse elif as nested if
            else_body = [self.if_stmt()]
        elif self.peek()[1] == "else":
            self.consume("KEYWORD", "else")
            else_body = self.block()
        
        return IfStatement(condition, then_body, else_body)

    def while_stmt(self):
        """Parse while loop"""
        self.consume("KEYWORD", "while")
        self.consume("LPAREN")
        condition = self.expr()
        self.consume("RPAREN")
        body = self.block()
        return WhileLoop(condition, body)

    def for_stmt(self):
        """Parse for loop (C-style or for-in)"""
        self.consume("KEYWORD", "for")
    
        # C-style for loop
        if self.peek()[0] == "LPAREN":
            self.consume("LPAREN")
            init = self.assignment_or_expr()
            self.consume("SEMICOL")
            condition = self.expr()
            self.consume("SEMICOL")
            update = self.assignment_or_expr()
            self.consume("RPAREN")
            body = self.block()
            return ForLoop(init, condition, update, body)
        # For-in loop
        elif self.peek()[0] == "ID":
            var_name = self.consume("ID")[1]
            self.consume("KEYWORD", "in")
            iterable = self.expr()
            body = self.block()
            return ForInLoop(var_name, iterable, body)
        else:
            raise ParseError(f"Invalid 'for' statement")

    def switch_stmt(self):
        """Parse switch statement"""
        self.consume("KEYWORD", "switch")
        self.consume("LPAREN")
        expr = self.expr()
        self.consume("RPAREN")
        self.consume("LBRACE")

        cases = []
        default_body = None

        while self.peek()[0] != "RBRACE":
            tok = self.peek()
            if tok[1] == "case":
                self.consume("KEYWORD", "case")
                case_expr = self.expr()
                self.consume("COLON")
                body = []
                while self.peek()[1] not in ("case", "default") and self.peek()[0] != "RBRACE":
                    body.append(self.statement())
                cases.append((case_expr, body))
            elif tok[1] == "default":
                self.consume("KEYWORD", "default")
                self.consume("COLON")
                default_body = []
                while self.peek()[0] != "RBRACE" and self.peek()[1] != "case":
                    default_body.append(self.statement())
            else:
                raise ParseError(f"Unexpected token in switch: {tok}")
            
        self.consume("RBRACE")
        return SwitchStatement(expr, cases, default_body)

    def match_stmt(self):
        """Parse pattern matching statement"""
        self.consume("KEYWORD", "match")
        # Parse just the value to match on (identifier or literal)
        tok = self.peek()
        if tok[0] == "ID":
            expr = Identifier(self.consume("ID")[1])
        elif tok[0] in ("NUMBER", "STRING", "BOOL", "NULL"):
            expr = self.primary()
        else:
            raise ParseError(f"Expected identifier or literal in match, got {tok}")
        
        self.consume("LBRACE")
        
        arms = []
        while self.peek()[0] != "RBRACE":
            pattern = self.pattern()
            guard = None
            
            # Optional guard: if condition
            if self.peek()[1] == "if":
                self.consume("KEYWORD", "if")
                guard = self.expr()
            
            self.consume("OP", "=>")
            
            # Body can be expression or block
            if self.peek()[0] == "LBRACE":
                body = self.block()
            else:
                body = [self.expr()]
            
            arms.append((pattern, guard, body))
            
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        
        self.consume("RBRACE")
        return MatchStatement(expr, arms)

    def pattern(self):
        """Parse a pattern for match expressions"""
        tok = self.peek()
        
        # Literal patterns - wrap in Literal node
        if tok[0] in ("NUMBER", "BOOL", "NULL", "CHAR", "STRING"):
            if tok[0] == "NUMBER":
                self.consume()
                value = int(tok[1]) if "." not in tok[1] else float(tok[1])
                return Literal(value)
            elif tok[0] == "BOOL":
                self.consume()
                return Literal(True if tok[1] == "true" else False)
            elif tok[0] == "NULL":
                self.consume()
                return NullLiteral()
            elif tok[0] in ("CHAR", "STRING"):
                self.consume()
                return Literal(tok[1].strip('"\''))
        # Wildcard pattern
        elif tok[1] == "_":
            self.consume()
            return Identifier("_")
        # Variable binding or enum variant
        elif tok[0] == "ID":
            name = self.consume("ID")[1]
            # Enum variant with data
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                inner_patterns = []
                while self.peek()[0] != "RPAREN":
                    inner_patterns.append(self.pattern())
                    if self.peek()[0] == "COMMA":
                        self.consume("COMMA")
                self.consume("RPAREN")
                return StructLiteral(name, inner_patterns)
            return Identifier(name)
        # Tuple pattern
        elif tok[0] == "LPAREN":
            return self.tuple_literal()
        # Array pattern
        elif tok[0] == "LBRACKET":
            return self.array_literal()
        else:
            raise ParseError(f"Invalid pattern: {tok}")

    def try_catch_stmt(self):
        """Parse try-catch with multiple catch clauses"""
        self.consume("KEYWORD", "try")
        try_block = self.block()

        catch_clauses = []
        while self.peek()[1] == "catch":
            self.consume("KEYWORD", "catch")
            
            exception_type = None
            catch_var = None
            
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                # Can specify exception type
                if self.peek(1)[0] == "ID":
                    exception_type = self.consume("ID")[1]
                catch_var = self.consume("ID")[1]
                self.consume("RPAREN")
            
            catch_block = self.block()
            catch_clauses.append((exception_type, catch_var, catch_block))

        finally_block = None
        if self.peek()[1] == "finally":
            self.consume("KEYWORD", "finally")
            finally_block = self.block()

        return TryCatchStatement(try_block, catch_clauses, finally_block)

    def struct_def(self):
        """Parse struct definition"""
        self.consume("KEYWORD", "struct")
        name = self.consume("ID")[1]
        self.consume("LBRACE")
        
        fields = []
        while self.peek()[0] != "RBRACE":
            field_name = self.consume("ID")[1]
            self.consume("COLON")
            field_type = self.consume("ID")[1]
            
            default_value = None
            if self.peek()[1] == "=":
                self.consume("OP", "=")
                default_value = self.expr()
            
            fields.append((field_name, field_type, default_value))
            
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        
        self.consume("RBRACE")
        return StructDef(name, fields)

    def enum_def(self):
        """Parse enum definition"""
        self.consume("KEYWORD", "enum")
        name = self.consume("ID")[1]
        self.consume("LBRACE")
        
        variants = []
        while self.peek()[0] != "RBRACE":
            variant_name = self.consume("ID")[1]
            
            associated_data = None
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                associated_data = []
                while self.peek()[0] != "RPAREN":
                    associated_data.append(self.consume("ID")[1])
                    if self.peek()[0] == "COMMA":
                        self.consume("COMMA")
                self.consume("RPAREN")
            
            variants.append((variant_name, associated_data))
            
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        
        self.consume("RBRACE")
        return EnumDef(name, variants)

    def type_alias(self):
        """Parse type alias"""
        self.consume("KEYWORD", "type")
        name = self.consume("ID")[1]
        self.consume("OP", "=")
        type_expr = self.consume("ID")[1]
        return TypeAlias(name, type_expr)

    def import_stmt(self):
        """Parse import statement"""
        self.consume("KEYWORD", "import")
        
        # from module import name
        if self.peek()[1] == "from":
            self.consume("KEYWORD", "from")
            module = self.consume("ID")[1]
            self.consume("KEYWORD", "import")
            names = []
            while True:
                names.append(self.consume("ID")[1])
                if self.peek()[0] != "COMMA":
                    break
                self.consume("COMMA")
            return ImportStatement(module, names)
        # import module [as alias]
        else:
            module = self.consume("ID")[1]
            alias = None
            if self.peek()[1] == "as":
                self.consume("KEYWORD", "as")
                alias = self.consume("ID")[1]
            return ImportStatement(module, alias=alias)

    def function_def(self):
        """Parse function definition with enhanced features"""
        is_async = False
        if self.peek()[1] == "async":
            self.consume("KEYWORD", "async")
            is_async = True
        
        self.consume("KEYWORD", "fnc")
        name = self.consume("ID")[1]
        self.consume("LPAREN")
        
        params = []
        while self.peek()[0] != "RPAREN":
            param_type = None
            
            # Type annotation
            if self.peek(1)[0] == "ID" and self.peek(1)[1] not in ("=", ",", ")"):
                param_type = self.consume("ID")[1]
            
            param_name = self.consume("ID")[1]
            
            # Default value
            default_value = None
            if self.peek()[1] == "=":
                self.consume("OP", "=")
                default_value = self.expr()
            
            params.append((param_type, param_name, default_value))
            
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        
        self.consume("RPAREN")
        
        # Return type annotation
        return_type = None
        if self.peek()[0] == "OP" and self.peek()[1] == "->":
            self.consume("OP", "->")
            return_type = self.consume("ID")[1]
        
        body = self.block()
        return FunctionDef(name, params, body, return_type, is_async)

    def print_stmt(self):
        """Parse print statement"""
        self.consume("KEYWORD", "print")
        self.consume("LPAREN")
        expr = self.expr()
        self.consume("RPAREN")
        return PrintStatement(expr)
    
    def printf_stmt(self):
        """Parse printf statement"""
        self.consume("KEYWORD", "printf")
        self.consume("LPAREN")
        format_expr = self.expr()
        args = []
        while self.peek()[0] == "COMMA":
            self.consume("COMMA")
            args.append(self.expr())
        self.consume("RPAREN")
        return PrintfStatement(format_expr, args)

    # ===== Expression Parsing =====

    def expr(self):
        """Parse expression starting from lowest precedence"""
        return self.ternary()

    def ternary(self):
        """Parse ternary operator: condition ? true_val : false_val"""
        expr = self.logic_or()
        if self.peek()[1] == "?":
            self.consume("OP", "?")
            true_val = self.expr()
            self.consume("COLON")
            false_val = self.expr()
            return TernaryOp(expr, true_val, false_val)
        return expr

    def logic_or(self):
        """Parse logical OR and XOR"""
        left = self.logic_and()
        while self.peek()[1] in ["or", "xor", "||"]:
            op = self.consume()[1]
            if op == "||":
                op = "or"
            right = self.logic_and()
            left = BinaryOp(left, op, right)
        return left

    def logic_and(self):
        """Parse logical AND"""
        left = self.logic_then()
        while self.peek()[1] in ["and", "&&"]:
            op = self.consume()[1]
            if op == "&&":
                op = "and"
            right = self.logic_then()
            left = BinaryOp(left, op, right)
        return left

    def logic_then(self):
        """Parse logical implication"""
        left = self.logic_nand()
        while self.peek()[1] == "then":
            op = self.consume()[1]
            right = self.logic_nand()
            left = BinaryOp(left, op, right)
        return left

    def logic_nand(self):
        """Parse NAND"""
        left = self.comparison()
        while self.peek()[1] == "nand":
            op = self.consume()[1]
            right = self.comparison()
            left = BinaryOp(left, op, right)
        return left
    
    def comparison(self):
        """Parse comparison operators"""
        left = self.bitwise_or()
        while self.peek()[1] in ["==", "!=", "<", ">", "<=", ">=", "in", "<=>", "===", "!=="]:
            op = self.consume()[1]
            right = self.bitwise_or()
            left = BinaryOp(left, op, right)
        return left

    def bitwise_or(self):
        """Parse bitwise OR"""
        left = self.bitwise_xor()
        while self.peek()[1] == "|":
            op = self.consume()[1]
            right = self.bitwise_xor()
            left = BinaryOp(left, op, right)
        return left

    def bitwise_xor(self):
        """Parse bitwise XOR"""
        left = self.bitwise_and()
        while self.peek()[1] == "^":
            op = self.consume()[1]
            right = self.bitwise_and()
            left = BinaryOp(left, op, right)
        return left

    def bitwise_and(self):
        """Parse bitwise AND"""
        left = self.shift()
        while self.peek()[1] == "&":
            op = self.consume()[1]
            right = self.shift()
            left = BinaryOp(left, op, right)
        return left

    def shift(self):
        """Parse bit shift operators"""
        left = self.range_expr()
        while self.peek()[1] in ["<<", ">>"]:
            op = self.consume()[1]
            right = self.range_expr()
            left = BinaryOp(left, op, right)
        return left

    def range_expr(self):
        """Parse range expressions: 1..10 or 1..=10"""
        left = self.addition()
        if self.peek()[1] == "..":
            self.consume("OP", "..")
            inclusive = False
            if self.peek()[1] == "=":
                self.consume("OP", "=")
                inclusive = True
            right = self.addition()
            return RangeLiteral(left, right, inclusive)
        elif self.peek()[1] == "..=":
            self.consume()
            right = self.addition()
            return RangeLiteral(left, right, inclusive=True)
        return left

    def addition(self):
        """Parse addition and subtraction"""
        left = self.multiplication()
        while self.peek()[1] in ("+", "-"):
            op = self.consume()[1]
            right = self.multiplication()
            left = BinaryOp(left, op, right)
        return left

    def multiplication(self):
        """Parse multiplication, division, and modulo"""
        left = self.power()
        while self.peek()[1] in ("*", "/", "%", "//"):
            op = self.consume()[1]
            right = self.power()
            left = BinaryOp(left, op, right)
        return left

    def power(self):
        """Parse exponentiation (right-associative)"""
        left = self.unary()
        if self.peek()[1] == "**":
            op = self.consume()[1]
            right = self.power()  # Right-associative
            return BinaryOp(left, op, right)
        return left

    def unary(self):
        """Parse unary operators"""
        tok = self.peek()

        if tok[0] == "OP" and tok[1] in ("+", "-", "~", "!"):
            op = self.consume()[1]
            if op == "!":
                op = "not"
            expr = self.unary()
            return UnaryOp(op, expr)

        if tok[1] == "not":
            self.consume()
            expr = self.unary()
            return UnaryOp("not", expr)
        
        # Increment/decrement operators
        if tok[1] in ("++", "--"):
            op = self.consume()[1]
            expr = self.unary()
            return UnaryOp(op, expr)
        
        # await keyword
        if tok[1] == "await":
            self.consume("KEYWORD", "await")
            expr = self.unary()
            return AwaitExpr(expr)

        return self.postfix()

    def postfix(self):
        """Parse postfix operations (member access, indexing, calls)"""
        expr = self.primary()
        
        while True:
            tok = self.peek()
            
            # Member access: obj.field
            if tok[0] == "DOT":
                self.consume("DOT")
                member = self.consume("ID")[1]
                
                # Method call
                if self.peek()[0] == "LPAREN":
                    self.consume("LPAREN")
                    args = []
                    while self.peek()[0] != "RPAREN":
                        args.append(self.expr())
                        if self.peek()[0] == "COMMA":
                            self.consume("COMMA")
                    self.consume("RPAREN")
                    expr = FunctionCall(MemberAccess(expr, member), args)
                else:
                    expr = MemberAccess(expr, member)
            
            # Array/dict indexing: expr[index]
            elif tok[0] == "LBRACKET":
                self.consume("LBRACKET")
                
                # Check for slicing: [start:end:step]
                start = self.expr() if self.peek()[0] != "COLON" else None
                
                if self.peek()[0] == "COLON":
                    self.consume("COLON")
                    end = self.expr() if self.peek()[0] not in ("COLON", "RBRACKET") else None
                    step = None
                    if self.peek()[0] == "COLON":
                        self.consume("COLON")
                        step = self.expr()
                    self.consume("RBRACKET")
                    expr = SliceAccess(expr, start, end, step)
                else:
                    self.consume("RBRACKET")
                    expr = IndexAccess(expr, start)
            
            # Postfix increment/decrement
            elif tok[1] in ("++", "--"):
                op = self.consume()[1]
                expr = UnaryOp(op + "_post", expr)
            
            else:
                break
        
        return expr

    def primary(self):
        """Parse primary expressions"""
        tok = self.peek()

        # Grouped expression or tuple
        if tok[0] == "LPAREN":
            start_pos = self.pos
            self.consume("LPAREN")
            
            # Empty tuple
            if self.peek()[0] == "RPAREN":
                self.consume("RPAREN")
                return TupleLiteral([])
            
            # Parse first element
            first = self.expr()
            
            # Single element with comma = 1-tuple
            if self.peek()[0] == "COMMA":
                elements = [first]
                while self.peek()[0] == "COMMA":
                    self.consume("COMMA")
                    if self.peek()[0] == "RPAREN":  # Trailing comma
                        break
                    elements.append(self.expr())
                self.consume("RPAREN")
                return TupleLiteral(elements)
            # No comma = grouped expression
            else:
                self.consume("RPAREN")
                return first

        # Numbers
        elif tok[0] == "NUMBER":
            self.consume()
            value = int(tok[1]) if "." not in tok[1] else float(tok[1])
            return Literal(value)
        
        elif tok[0] == "FLOAT":
            self.consume()
            return Literal(float(tok[1]))
        
        elif tok[0] in ("INT_HEX", "INT_OCTAL", "INT_BINARY"):
            self.consume()
            value = int(tok[1], 0)  # Auto-detect base
            return Literal(value)

        # Arrays
        elif tok[0] == "LBRACKET":
            return self.array_literal()
        
        # Dictionaries and sets
        elif tok[0] == "LBRACE":
            # Look ahead to distinguish dict from set
            if self.peek(1)[0] == "RBRACE":
                # Empty dict {}
                self.consume("LBRACE")
                self.consume("RBRACE")
                return DictLiteral([])
            elif self.peek(2)[0] == "COLON":
                return self.dict_literal()
            else:
                return self.set_literal()

        # Literals
        elif tok[0] == "BOOL":
            self.consume()
            return Literal(True if tok[1] == "true" else False)
        
        elif tok[0] == "NULL":
            self.consume("NULL")
            return NullLiteral()
        
        elif tok[0] == "STRING":
            self.consume()
            return Literal(tok[1].strip('"'))
        
        elif tok[0] == "STRING_INTERP":
            return self.string_interpolation(tok[1])
        
        elif tok[0] == "CHAR":
            self.consume()
            return CharLiteral(tok[1][1:-1])
        
        elif tok[0] == "BIGINT":
            self.consume("BIGINT")
            return BigIntLiteral(tok[1])
        
        elif tok[0] == "DECIMAL":
            self.consume()
            return DecimalLiteral(tok[1][:-1])

        # Type constructors
        elif tok[0] == "ID" and tok[1] in ("int8", "int16", "int32", "int64", "int128", "int256"):
            typename = self.consume("ID")[1]
            self.consume("LPAREN")
            inner_expr = self.expr()
            self.consume("RPAREN")
            bit_size = int(typename[3:])
            return IntLiteral(inner_expr, bit_size, signed=True)
        
        elif tok[0] == "ID" and tok[1] in ("uint8", "uint16", "uint32", "uint64", "uint128", "uint256"):
            typename = self.consume("ID")[1]
            self.consume("LPAREN")
            inner_expr = self.expr()
            self.consume("RPAREN")
            bit_size = int(typename[4:])
            return UIntLiteral(inner_expr, bit_size)

        elif tok[0] == "ID" and tok[1] in ("usize", "isize"):
            typename = self.consume("ID")[1]
            self.consume("LPAREN")
            inner_expr = self.expr()
            self.consume("RPAREN")
            return SizeIntLiteral(inner_expr, signed=(typename == "isize"))

        elif tok[0] == "ID" and tok[1] == "ptrdiff":
            self.consume("ID")
            self.consume("LPAREN")
            inner_expr = self.expr()
            self.consume("RPAREN")
            return PtrDiffLiteral(inner_expr)

        # Lambda expressions: |x, y| x + y
        elif tok[0] == "OP" and tok[1] == "|":
            return self.lambda_expr()

        # Identifiers and function calls
        elif tok[0] == "ID":
            name = self.consume("ID")[1]
            
            # Function call
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                args = []
                kwargs = {}
                
                while self.peek()[0] != "RPAREN":
                    # Named argument: name = value
                    if self.peek()[0] == "ID" and self.peek(1)[1] == "=":
                        arg_name = self.consume("ID")[1]
                        self.consume("OP", "=")
                        kwargs[arg_name] = self.expr()
                    else:
                        args.append(self.expr())
                    
                    if self.peek()[0] == "COMMA":
                        self.consume("COMMA")
                
                self.consume("RPAREN")
                return FunctionCall(name, args, kwargs)
            
            # Struct literal: Person { name: "Alice", age: 30 }
            elif self.peek()[0] == "LBRACE":
                self.consume("LBRACE")
                fields = {}
                while self.peek()[0] != "RBRACE":
                    field_name = self.consume("ID")[1]
                    self.consume("COLON")
                    field_value = self.expr()
                    fields[field_name] = field_value
                    if self.peek()[0] == "COMMA":
                        self.consume("COMMA")
                self.consume("RBRACE")
                return StructLiteral(name, fields)
            
            else:
                return Identifier(name)

        else:
            raise ParseError(f"Unexpected token in primary(): {tok}")

    def lambda_expr(self):
        """Parse lambda expression: |x, y| x + y"""
        self.consume("OP", "|")
        params = []
        while self.peek()[0] != "OP" or self.peek()[1] != "|":
            params.append(self.consume("ID")[1])
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        self.consume("OP", "|")
        body = self.expr()
        return LambdaExpr(params, body)

    def string_interpolation(self, raw_string):
        """Parse string interpolation: f"Hello {name}" """
        # Simple implementation - can be enhanced
        parts = []
        # Remove f" and "
        content = raw_string[2:-1]
        # Split by {}, parse expressions
        # This is a simplified version
        parts.append(Literal(content))
        return StringInterpolation(parts)

    def array_literal(self):
        """Parse array literal"""
        self.consume("LBRACKET")
        elements = []
        while self.peek()[0] != "RBRACKET":
            elements.append(self.expr())
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACKET")
        return ArrayLiteral(elements)
    
    def dict_literal(self):
        """Parse dictionary literal"""
        self.consume("LBRACE")
        pairs = []
        while self.peek()[0] != "RBRACE":
            key = self.expr()
            self.consume("COLON")
            value = self.expr()
            pairs.append((key, value))
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACE")
        return DictLiteral(pairs)

    def set_literal(self):
        """Parse set literal"""
        self.consume("LBRACE")
        elements = []
        while self.peek()[0] != "RBRACE":
            elements.append(self.expr())
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACE")
        return SetLiteral(elements)

    def tuple_literal(self):
        """Parse tuple literal (handled in primary now)"""
        # This is kept for compatibility but primary() handles it
        return self.primary()