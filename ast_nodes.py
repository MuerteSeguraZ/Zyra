class Node:
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(Node):
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

class Assignment(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Identifier(Node):
    def __init__(self, name):
        self.name = name

class Literal(Node):
    def __init__(self, value):
        self.value = value

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class IfStatement(Node):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileLoop(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForLoop(Node):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class PrintStatement(Node):
    def __init__(self, expr):
        self.expr = expr

class FunctionDef(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of (type, name)
        self.body = body

class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ReturnStatement(Node):
    def __init__(self, expr):
        self.expr = expr

class BreakStatement(Node):
    pass

class ContinueStatement(Node):
    pass
