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
        var_type = self.consume("ID")[1]
        name = self.consume("ID")[1]
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
            elif self.peek()[0] == "LPAREN":
                # function call
                self.pos -= 1  # step back so term() can handle it
                return self.term()
            else:
                return Identifier(name)
        else:
            return self.expr()

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
        self.consume("LPAREN")
        init = self.assignment_or_expr()
        self.consume("SEMICOL")
        condition = self.expr()
        self.consume("SEMICOL")
        update = self.assignment_or_expr()
        self.consume("RPAREN")
        body = self.block()
        return ForLoop(init, condition, update, body)

    def print_stmt(self):
        self.consume(None, "print")
        self.consume("LPAREN")
        expr = self.expr()
        self.consume("RPAREN")
        return PrintStatement(expr)
    
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
        return self.logic_or()

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
        while self.peek()[1] in ["+", "-"]:
            op = self.consume()[1]
            right = self.term()
            left = BinaryOp(left, op, right)
        return left

    def term(self):
        left = self.factor()
        while self.peek()[1] in ["*", "/"]:
            op = self.consume()[1]
            right = self.factor()
            left = BinaryOp(left, op, right)
        return left

    def factor(self):
        tok = self.peek()
        if tok[1] == "not":
            self.consume()
            expr = self.factor()  # recursion ensures "not not true" works
            return UnaryOp("not", expr)
        elif tok[0] == "NUMBER":
            self.consume()
            return Literal(float(tok[1]) if "." in tok[1] else int(tok[1]))
        elif tok[0] == "STRING":
            self.consume()
            return Literal(tok[1].strip('"'))
        elif tok[0] == "BOOL":
            self.consume()
            return Literal(True if tok[1] == "true" else False)
        elif tok[0] == "ID":
            name = self.consume("ID")[1]
            if self.peek()[0] == "LPAREN":
                self.consume("LPAREN")
                args = []
                while self.peek()[0] != "RPAREN":
                    args.append(self.expr())
                    if self.peek()[0] == "COMMA":
                        self.consume("COMMA")
                self.consume("RPAREN")
                return FunctionCall(name, args)
            else:
                return Identifier(name)
        elif tok[0] == "LPAREN":
            self.consume("LPAREN")
            expr = self.expr()
            self.consume("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token in factor: {tok}")