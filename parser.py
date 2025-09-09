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
        else:
            return self.expr()
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
    
    def function_def(self):
        self.consume(None, "fnc")
        name = self.consume("ID")[1]
        self.consume("LPAREN")
        params = []
        while self.peek()[0] != "RPAREN":
            param_type = self.consume("ID")[1]
            param_name = self.consume("ID")[1]
            params.append((param_type, param_name))
            if self.peek()[0] == "COMMA":
                self.consume("COMMA")
        self.consume("RPAREN")
        body = self.block()
        return FunctionDef(name, params, body)

    def expr(self):
      left = self.term()
      while self.peek()[1] in ["+", "-", "==", "<", ">", "<=", ">="]:
        op = self.consume()[1]
        right = self.term()
        left = BinaryOp(left, op, right)

      return left

    def term(self):
      tok = self.peek()
      if tok[0] == "NUMBER":
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
        # check for function call
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
        raise SyntaxError(f"Unexpected token in term: {tok}")
