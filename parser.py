from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected_type=None, expected_value=None):
        tok = self.peek()
        if expected_type and tok[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {tok}")
        if expected_value and tok[1] != expected_value:
            raise SyntaxError(f"Expected {expected_value}, got {tok}")
        self.pos += 1
        return tok

    def parse(self):
        statements = []
        while self.peek()[0] is not None:
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        tok = self.peek()
        if tok[1] == "dec":
            return self.var_decl()
        elif tok[1] == "if":
            return self.if_stmt()
        elif tok[1] == "while":
            return self.while_stmt()
        elif tok[1] == "for":
            return self.for_stmt()
        elif tok[1] == "print":
            return self.print_stmt()
        elif tok[1] == "printf":
            return self.printf_stmt()
        elif tok[1] == "fnc":
            return self.function_def()
        elif tok[1] == "return":
            self.consume(None, "return")
            expr = self.expr()
            return ReturnStatement(expr)
        elif tok[1] == "break":
            self.consume(None, "break")
            return BreakStatement()
        elif tok[1] == "continue":
            self.consume(None, "continue")
            return ContinueStatement()
        elif tok[1] == "switch":
            return self.switch_stmt()
        elif tok[1] == "try":
            return self.try_catch_stmt()
        elif tok[1] == "throw":
            self.consume(None, "throw")
            expr = self.expr()
            return ThrowStatement(expr)
        else:
            return self.assignment_or_expr()

    def block(self):
        self.consume("LBRACE")
        stmts = []
        while self.peek()[0] != "RBRACE":
            stmts.append(self.statement())
        self.consume("RBRACE")
        return stmts

    def var_decl(self):
        self.consume(None, "dec")
        first_id = self.consume("ID")[1]

        if self.peek()[0] == "ID":
            var_type = first_id
            name = self.consume("ID")[1]
        else:
            var_type = None
            name = first_id

            self.consume("OP", "=")
            value = self.expr()
            return VarDecl(var_type, name, value)

    def assignment_or_expr(self):
            tok = self.peek()

            if tok[0] == "ID":
                name = self.consume("ID")[1]

                if self.peek()[1] == "=":
                    self.consume("OP", "=")
                    value = self.expr()
                    return Assignment(name, value)

                elif self.peek()[1] in ["+=", "-=", "*=", "/="]:
                    op = self.consume()[1]
                    value = self.expr()
                    return AugmentedAssignment(name, op, value)

                elif self.peek()[0] == "LPAREN":
                    self.pos -= 1
                    return self.term()

                else:
                    return Identifier(name)
            else:
                expr_node = self.expr()
                return expr_node

    def if_stmt(self):
        self.consume(None, "if")
        self.consume("LPAREN")
        condition = self.expr()
        self.consume("RPAREN")
        then_body = self.block()
        else_body = None
        if self.peek()[1] == "else":
            self.consume()
            else_body = self.block()
        return IfStatement(condition, then_body, else_body)

    def while_stmt(self):
        self.consume(None, "while")
        self.consume("LPAREN")
        condition = self.expr()
        self.consume("RPAREN")
        body = self.block()
        return WhileLoop(condition, body)

    def for_stmt(self):
        self.consume(None, "for")
    
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

        elif self.peek()[0] == "ID" and self.tokens[self.pos+1][1] == "in":
            var_name = self.consume("ID")[1]
            self.consume(None, "in")
            iterable = self.expr()
            body = self.block()
            return ForInLoop(var_name, iterable, body)
        else:
            raise SyntaxError(f"Invalid 'for' statement at token {self.peek()}")

        
    def array_literal(self):
        self.consume("LBRACKET")
        elements = []
        while self.peek()[0] != "RBRACKET":
            elements.append(self.expr())
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACKET")
        return ArrayLiteral(elements)
    
    def dict_literal(self):
        self.consume("LBRACE")  # {
        pairs = []

        while self.peek()[0] != "RBRACE":  # }
            key = self.expr()
            self.consume("COLON")
            value = self.expr()
            pairs.append((key, value))
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
            else:
                break

        self.consume("RBRACE")
        return DictLiteral(pairs)
    
    def tuple_literal(self):
            self.consume("LPAREN")
            elements = []

            if self.peek()[0] == "RPAREN":  # empty tuple
                self.consume("RPAREN")
                return TupleLiteral(elements)

            while True:
                elements.append(self.expr())
                tok = self.peek()
                if tok[0] == "COMMA":
                    self.consume("COMMA")
            # continue parsing next element (handle trailing comma automatically)
                    if self.peek()[0] == "RPAREN":  # trailing comma
                        self.consume("RPAREN")
                        break
                elif tok[0] == "RPAREN":
                    self.consume("RPAREN")
                    break
                else:
                    raise SyntaxError(f"Expected ',' or ')', got {tok}")

            return TupleLiteral(elements)

    def set_literal(self):
        self.consume("LBRACE")
        elements = []
        while self.peek()[0] != "RBRACE":
            elements.append(self.expr())
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
            self.consume("RBRACE")
            return SetLiteral(elements)

    def print_stmt(self):
        self.consume(None, "print")
        self.consume("LPAREN")
        expr = self.expr()
        self.consume("RPAREN")
        return PrintStatement(expr)
    
    def printf_stmt(self):
        self.consume(None, "printf")
        self.consume("LPAREN")
    
        format_expr = self.expr()  # first argument is the format string
        args = []
    
        while self.peek()[0] == "COMMA":
            self.consume("COMMA")
            args.append(self.expr())
    
        self.consume("RPAREN")
        return PrintfStatement(format_expr, args)

    def try_catch_stmt(self):
        self.consume(None, "try")
        try_block = self.block()

        self.consume(None, "catch")
        catch_var = None
        if self.peek()[0] == "LPAREN":
            self.consume("LPAREN")
            catch_var = self.consume("ID")[1]
            self.consume("RPAREN")
        catch_block = self.block()

        return TryCatchStatement(try_block, catch_var, catch_block)
    
    def switch_stmt(self):
        self.consume(None, "switch")
        self.consume("LPAREN")
        expr = self.expr()
        self.consume("RPAREN")
        self.consume("LBRACE")

        cases = []
        default_body = None

        while self.peek()[0] != "RBRACE":
            tok = self.peek()
            if tok[1] == "case":
                self.consume()
                case_expr = self.expr()
                self.consume("COLON")
                body = []
                while self.peek()[1] not in ("case", "default", "}"):
                    body.append(self.statement())
                cases.append((case_expr, body))
            elif tok[1] == "default":
                self.consume()
                self.consume("COLON")
                default_body = []
                while self.peek()[1] != "}":
                    default_body.append(self.statement())
            else:
                raise SyntaxError(f"Unexpected token in switch: {tok}")
            
        self.consume("RBRACE")
        return SwitchStatement(expr, cases, default_body)

    def function_def(self):
      self.consume(None, "fnc")
      name = self.consume("ID")[1]
      self.consume("LPAREN")
      params = []
      while self.peek()[0] != "RPAREN":
        # Check if type is present or just a name
        next_tok = self.peek()
        param_type = None
        param_name = None
        if next_tok[0] == "ID":
            # Consume first ID
            first_id = self.consume("ID")[1]
            # If next is also ID, treat as type+name
            if self.peek()[0] == "ID":
                param_type = first_id
                param_name = self.consume("ID")[1]
            else:
                # Only a name, no type
                param_name = first_id
        params.append((param_type, param_name))
        if self.peek()[0] == "COMMA":
            self.consume("COMMA")
      self.consume("RPAREN")
      body = self.block()
      return FunctionDef(name, params, body)

    # ----- Expressions -----
    def expr(self):
    # Start parsing with full precedence (addition/subtraction, multiplication/division, etc.)
        return self.logic_or()

    def primary(self):
        tok = self.peek()

        # --- Tuple / grouped expressions ---
        if tok[0] == "LPAREN":
            node = self.tuple_literal()  # handles (), (1,), (1,2,3), nested
        # --- Number literal ---
        elif tok[0] == "NUMBER":
            self.consume()
            node = Literal(float(tok[1]) if "." in tok[1] else int(tok[1]))
        # --- Identifier ---
        elif tok[0] == "ID":
            name = self.consume("ID")[1]
            node = Identifier(name)

            # Function call
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                args = []
                while self.peek()[0] != "RPAREN":
                    args.append(self.expr())
                    if self.peek()[0] == "COMMA":
                        self.consume("COMMA")
                self.consume("RPAREN")
                node = FunctionCall(name, args)

        # --- Array literal ---
        elif tok[0] == "LBRACKET":
            node = self.array_literal()
        # --- Dictionary literal ---
        elif tok[0] == "LBRACE":
            node = self.dict_literal()
        # --- Boolean / null / string / char / bigint / decimal literals ---
        elif tok[0] == "BOOL":
            self.consume()
            node = Literal(True if tok[1] == "true" else False)
        elif tok[0] == "NULL":
            self.consume("NULL")
            node = NullLiteral()
        elif tok[0] == "STRING":
            self.consume()
            node = Literal(tok[1].strip('"'))
        elif tok[0] == "CHAR":
            self.consume()
            node = CharLiteral(tok[1][1:-1])
        elif tok[0] == "BIGINT":
            self.consume("BIGINT")
            node = BigIntLiteral(tok[1])
        elif tok[0] == "DECIMAL":
            self.consume()
            node = DecimalLiteral(tok[1][:-1])
        # --- Unary operators handled in factor() ---
        else:
        # fallback to logic_or if nothing matched
         node = self.logic_or()

        # --- Handle indexing / subscript: a[expr][expr]...
        while self.peek()[0] == "LBRACKET":
            self.consume("LBRACKET")
            index_expr = self.expr()
            self.consume("RBRACKET")
            node = IndexAccess(node, index_expr)

        return node

    def logic_or(self):
        left = self.logic_and()
        while self.peek()[1] in ["or", "xor"]:
            op = self.consume()[1]
            right = self.logic_and()
            left = BinaryOp(left, op, right)
        return left

    def logic_and(self):
        left = self.logic_then()
        while self.peek()[1] == "and":
            op = self.consume()[1]
            right = self.logic_then()
            left = BinaryOp(left, op, right)
        return left

    def logic_then(self):
        left = self.logic_nand()
        while self.peek()[1] == "then":
            op = self.consume()[1]
            right = self.logic_nand()
            left = BinaryOp(left, op, right)
        return left

    def logic_nand(self):
        left = self.comparison()
        while self.peek()[1] == "nand":
            op = self.consume()[1]
            right = self.comparison()
            left = BinaryOp(left, op, right)
        return left

    def comparison(self):
        left = self.addition()
        while self.peek()[1] in ["==", "<", ">", "<=", ">="]:
            op = self.consume()[1]
            right = self.addition()
            left = BinaryOp(left, op, right)
        return left

    def addition(self):
            left = self.term()
            while True:
                tok = self.peek()
                if tok and tok[0] == "OP" and tok[1] in ("+", "-"):
                    op = self.consume()[1]
                    right = self.term()
                    left = BinaryOp(left, op, right)
                else:
                    break
            return left

    def term(self):
            left = self.factor()
            while True:
                tok = self.peek()
                if tok and tok[0] == "OP" and tok[1] in ("*", "/"):
                    op = self.consume()[1]
                    right = self.factor()
                    left = BinaryOp(left, op, right)
                else:
                    break
            return left

    def factor(self):
        tok = self.peek()

        # Unary operators
        if tok[0] == "OP" and tok[1] in ("+", "-", "~"):
            op = self.consume()[1]
            expr = self.factor()  # recursive for multiple unary ops
            return UnaryOp(op, expr)

        if tok[1] == "not":
            self.consume()
            expr = self.factor()
            return UnaryOp("not", expr)

    # Delegate everything else to primary() which returns a node
        return self.primary()

