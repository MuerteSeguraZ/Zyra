from decimal import Decimal

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

class AugmentedAssignment:
    def __init__(self, name, operator, value):
        self.name = name
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"AugmentedAssignment({self.name}, {self.operator}, {self.value})"

class Identifier(Node):
    def __init__(self, name):
        self.name = name

class Literal(Node):
    def __init__(self, value):
        self.value = value

class ArrayLiteral(Node):
    def __init__(self, elements):
        self.elements = elements

class NullLiteral(Node):
    def __init__(self):
        self.value = None

class DictLiteral(Node):
    def __init__(self, pairs):
        self.pairs = pairs

class CharLiteral:
    def __init__(self, value):
        self.value = value  # string, either 1 char or escape like \n

    def __repr__(self):
        return f"CharLiteral({self.value!r})"
    
class BigIntLiteral:
    def __init__(self, value):
        self.value = int(value[:-1])  # strip the 'n' here

class DecimalLiteral:
    def __init__(self, value):
        self.value = Decimal(value)

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

class ForInLoop(Node):
    def __init__(self, var_name, iterable, body):
        self.var_name = var_name
        self.iterable = iterable
        self.body = body

class PrintStatement(Node):
    def __init__(self, expr):
        self.expr = expr

class PrintfStatement(Node):
    def __init__(self, format_expr, args):
        self.format_expr = format_expr  # the first string expression
        self.args = args                # list of remaining expressions

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

class SwitchStatement:
    def __init__(self, expr, cases, default=None):
        self.expr = expr
        self.cases = cases # tuples
        self.default = default

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class TryCatchStatement:
    def __init__(self, try_block, catch_var, catch_block):
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block

class ThrowStatement:
    def __init__(self, expr):
        self.expr = expr

class NativeFunction:
    def __init__(self, func):
        self.func = func

class IndexAccess(Node):
    def __init__(self, collection, index):
        self.collection = collection  # e.g., Identifier("person")
        self.index = index            # expression for the key/index

