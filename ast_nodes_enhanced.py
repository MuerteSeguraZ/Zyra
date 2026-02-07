from decimal import Decimal
from typing import Any, Optional, List, Tuple

class Node:
    """Base AST node with optional position tracking"""
    def __init__(self, line=None, column=None):
        self.line = line
        self.column = column

class Program(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements

# ===== Variable Declarations =====

class VarDecl(Node):
    def __init__(self, var_type, name, value, is_const=False, is_mut=True):
        super().__init__()
        self.var_type = var_type  # "uint8", "uint16", etc. or None
        self.name = name
        self.value = value
        self.is_const = is_const  # const declarations
        self.is_mut = is_mut      # mutable vs immutable

    def __repr__(self):
        qualifier = "const" if self.is_const else ("mut" if self.is_mut else "")
        return f"VarDecl({qualifier} {self.var_type}, {self.name}, {self.value})"

class Assignment(Node):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value

class AugmentedAssignment(Node):
    def __init__(self, name, operator, value):
        super().__init__()
        self.name = name
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"AugmentedAssignment({self.name}, {self.operator}, {self.value})"

class DestructuringAssignment(Node):
    """For pattern-based assignment: let (a, b, c) = tuple"""
    def __init__(self, pattern, value):
        super().__init__()
        self.pattern = pattern  # list of names or nested patterns
        self.value = value

# ===== Literals =====

class Identifier(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

class Literal(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class ArrayLiteral(Node):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

class NullLiteral(Node):
    def __init__(self):
        super().__init__()
        self.value = None

class DictLiteral(Node):
    def __init__(self, pairs):
        super().__init__()
        self.pairs = pairs

class CharLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value  # string, either 1 char or escape like \n

    def __repr__(self):
        return f"CharLiteral({self.value!r})"
    
class BigIntLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = int(value[:-1]) if isinstance(value, str) else value

class SizeIntLiteral(Node):
    def __init__(self, expr, signed=True):
        super().__init__()
        self.expr = expr
        self.signed = signed

    def __repr__(self):
        return f"{'isize' if self.signed else 'usize'}({self.expr})"

class DecimalLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = Decimal(value)

class TupleLiteral(Node):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def __repr__(self):
        return f"TupleLiteral({self.elements})"

class SetLiteral(Node):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def __repr__(self):
        return f"SetLiteral({self.elements})"

class RangeLiteral(Node):
    """Range literal: 1..10 or 1..=10 (inclusive)"""
    def __init__(self, start, end, inclusive=False):
        super().__init__()
        self.start = start
        self.end = end
        self.inclusive = inclusive

class StringInterpolation(Node):
    """f"Hello {name}" style strings"""
    def __init__(self, parts):
        super().__init__()
        self.parts = parts  # list of strings and expressions

# ===== Integer Types =====

class UIntLiteral(Node):
    def __init__(self, value, bit_size):
        super().__init__()
        self.value = value
        self.bit_size = bit_size

    def __repr__(self):
        return f"UIntLiteral({self.value}, {self.bit_size})"
    
class IntLiteral(Node):
    def __init__(self, value, bits, signed):
        super().__init__()
        self.value = value
        self.bits = bits
        self.signed = signed

class PtrDiffLiteral(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __repr__(self):
        return f"PtrDiffLiteral({self.expr})"

# ===== Operators =====

class BinaryOp(Node):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, expr):
        super().__init__()
        self.op = op
        self.expr = expr

class TernaryOp(Node):
    """condition ? true_val : false_val"""
    def __init__(self, condition, true_val, false_val):
        super().__init__()
        self.condition = condition
        self.true_val = true_val
        self.false_val = false_val

# ===== Control Flow =====

class IfStatement(Node):
    def __init__(self, condition, then_body, else_body=None):
        super().__init__()
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileLoop(Node):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

class ForLoop(Node):
    def __init__(self, init, condition, update, body):
        super().__init__()
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class ForInLoop(Node):
    def __init__(self, var_name, iterable, body):
        super().__init__()
        self.var_name = var_name
        self.iterable = iterable
        self.body = body

class SwitchStatement(Node):
    def __init__(self, expr, cases, default=None):
        super().__init__()
        self.expr = expr
        self.cases = cases
        self.default = default

class MatchStatement(Node):
    """Pattern matching: match expr { pattern => body, ... }"""
    def __init__(self, expr, arms):
        super().__init__()
        self.expr = expr
        self.arms = arms  # list of (pattern, guard, body)

class BreakStatement(Node):
    def __init__(self, value=None):
        super().__init__()
        self.value = value  # break can return a value

class ContinueStatement(Node):
    pass

class ReturnStatement(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

# ===== Functions =====

class FunctionDef(Node):
    def __init__(self, name, params, body, return_type=None, is_async=False):
        super().__init__()
        self.name = name
        self.params = params  # list of (type, name, default_value)
        self.body = body
        self.return_type = return_type
        self.is_async = is_async

class FunctionCall(Node):
    def __init__(self, name, args, kwargs=None):
        super().__init__()
        self.name = name
        self.args = args
        self.kwargs = kwargs or {}  # named arguments

class LambdaExpr(Node):
    """Lambda/anonymous functions: |x, y| x + y"""
    def __init__(self, params, body):
        super().__init__()
        self.params = params
        self.body = body

class YieldStatement(Node):
    """Generator yield"""
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

class AwaitExpr(Node):
    """Async/await"""
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

# ===== I/O =====

class PrintStatement(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

class PrintfStatement(Node):
    def __init__(self, format_expr, args):
        super().__init__()
        self.format_expr = format_expr
        self.args = args

# ===== Error Handling =====

class TryCatchStatement(Node):
    def __init__(self, try_block, catch_clauses, finally_block=None):
        super().__init__()
        self.try_block = try_block
        self.catch_clauses = catch_clauses  # list of (exception_type, var, block)
        self.finally_block = finally_block

class ThrowStatement(Node):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

# ===== Data Structures =====

class StructDef(Node):
    """struct Person { name: String, age: int32 }"""
    def __init__(self, name, fields):
        super().__init__()
        self.name = name
        self.fields = fields  # list of (field_name, type, default_value)

class EnumDef(Node):
    """enum Color { Red, Green, Blue }"""
    def __init__(self, name, variants):
        super().__init__()
        self.name = name
        self.variants = variants  # list of (variant_name, associated_data)

class TraitDef(Node):
    """trait Drawable { fnc draw(); }"""
    def __init__(self, name, methods):
        super().__init__()
        self.name = name
        self.methods = methods

class ImplBlock(Node):
    """impl Drawable for Circle { ... }"""
    def __init__(self, trait_name, type_name, methods):
        super().__init__()
        self.trait_name = trait_name
        self.type_name = type_name
        self.methods = methods

class StructLiteral(Node):
    """Person { name: "Alice", age: 30 }"""
    def __init__(self, struct_name, fields):
        super().__init__()
        self.struct_name = struct_name
        self.fields = fields  # dict or list of (name, value)

# ===== Member Access =====

class IndexAccess(Node):
    def __init__(self, collection, index):
        super().__init__()
        self.collection = collection
        self.index = index

class MemberAccess(Node):
    """obj.field or obj.method()"""
    def __init__(self, obj, member):
        super().__init__()
        self.obj = obj
        self.member = member

class SliceAccess(Node):
    """array[start:end:step]"""
    def __init__(self, collection, start, end, step=None):
        super().__init__()
        self.collection = collection
        self.start = start
        self.end = end
        self.step = step

# ===== Modules & Imports =====

class ImportStatement(Node):
    """import module or from module import name"""
    def __init__(self, module, names=None, alias=None):
        super().__init__()
        self.module = module
        self.names = names  # specific names to import
        self.alias = alias

class ExportStatement(Node):
    """export fnc or export const"""
    def __init__(self, declaration):
        super().__init__()
        self.declaration = declaration

# ===== Type Aliases =====

class TypeAlias(Node):
    """type UserId = uint64"""
    def __init__(self, name, type_expr):
        super().__init__()
        self.name = name
        self.type_expr = type_expr

# ===== Decorators/Attributes =====

class Decorator(Node):
    """@decorator or @decorator(args)"""
    def __init__(self, name, args=None):
        super().__init__()
        self.name = name
        self.args = args or []

# ===== Special =====

class NativeFunction(Node):
    """Wrapper for built-in functions"""
    def __init__(self, func):
        super().__init__()
        self.func = func

class MacroDef(Node):
    """macro name(args) { body }"""
    def __init__(self, name, params, body):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body

class CompilerDirective(Node):
    """#[inline], #[no_mangle], etc."""
    def __init__(self, directive, args=None):
        super().__init__()
        self.directive = directive
        self.args = args or []