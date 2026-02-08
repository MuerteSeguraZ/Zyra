from ast_nodes_enhanced import *
from decimal import Decimal
import operator

# ===== Runtime Exceptions =====

class RuntimeError(Exception):
    """Enhanced runtime error with position info"""
    def __init__(self, message, node=None):
        self.message = message
        self.node = node
        if node and hasattr(node, 'line'):
            super().__init__(f"{message} at line {node.line}")
        else:
            super().__init__(message)

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    def __init__(self, value=None):
        self.value = value

class ContinueException(Exception):
    pass

# ===== Runtime Objects =====

class Function:
    """User-defined function"""
    def __init__(self, def_node, env):
        self.def_node = def_node
        self.env = env  # Closure environment
        self.is_async = def_node.is_async if hasattr(def_node, 'is_async') else False

class Lambda:
    """Lambda/anonymous function"""
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

class Struct:
    """Runtime struct instance"""
    def __init__(self, struct_name, fields):
        self.struct_name = struct_name
        self.fields = fields  # dict of field_name -> value
    
    def __repr__(self):
        return f"{self.struct_name} {self.fields}"
    
class Union:
    """Runtime union instance - only one field is active at a time"""
    def __init__(self, union_name, active_field, value):
        self.union_name = union_name
        self.active_field = active_field  # which field is currently set
        self.value = value  # the value of the active field
    
    def __repr__(self):
        return f"{self.union_name}::{self.active_field} = {self.value}"

class Enum:
    """Runtime enum variant"""
    def __init__(self, enum_name, variant_name, data=None):
        self.enum_name = enum_name
        self.variant_name = variant_name
        self.data = data
    
    def __repr__(self):
        if self.data:
            return f"{self.enum_name}::{self.variant_name}({self.data})"
        return f"{self.enum_name}::{self.variant_name}"

class Range:
    """Range object for iteration"""
    def __init__(self, start, end, inclusive=False):
        self.start = start
        self.end = end
        self.inclusive = inclusive
    
    def __iter__(self):
        if self.inclusive:
            return iter(range(self.start, self.end + 1))
        return iter(range(self.start, self.end))

# ===== Environment =====

class Environment:
    """Enhanced environment with type tracking and scoping"""
    def __init__(self, parent=None):
        self.vars = {}  # name -> (value, type, is_const, is_mut)
        self.parent = parent
        self.structs = {}  # struct definitions
        self.unions = {}   # union definitions - INITIALIZE THIS!
        self.enums = {}    # enum definitions
        self.types = {}    # type aliases

    def get(self, name):
        """Get variable value"""
        if name in self.vars:
            return self.vars[name][0]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise RuntimeError(f"Variable '{name}' not defined")

    def get_type(self, name):
        """Get variable type"""
        if name in self.vars:
            return self.vars[name][1]
        elif self.parent:
            return self.parent.get_type(name)
        else:
            return None

    def is_const(self, name):
        """Check if variable is constant"""
        if name in self.vars:
            return self.vars[name][2]
        elif self.parent:
            return self.parent.is_const(name)
        return False

    def define(self, name, value, var_type=None, is_const=False, is_mut=True):
        """Define a new variable (allows shadowing)"""
        # Apply type wrapping
        if var_type:
            value = self.wrap_type(value, var_type)
        
        self.vars[name] = (value, var_type, is_const, is_mut)

    def set(self, name, value):
        """Update variable value"""
        if name in self.vars:
            _, var_type, is_const, is_mut = self.vars[name]
            
            if is_const:
                raise RuntimeError(f"Cannot assign to const variable '{name}'")
            if not is_mut:
                raise RuntimeError(f"Cannot assign to immutable variable '{name}'")
            
            # Apply type wrapping
            if var_type:
                value = self.wrap_type(value, var_type)
            
            self.vars[name] = (value, var_type, is_const, is_mut)
        elif self.parent:
            self.parent.set(name, value)
        else:
            # Auto-define if doesn't exist (for loop variables, etc.)
            self.define(name, value)

    def wrap_type(self, value, var_type):
        """Apply type constraints (wrapping for integer types)"""
        if var_type in ("uint8", "uint16", "uint32", "uint64", "uint128", "uint256"):
            bit_size = int(var_type[4:])
            mask = (1 << bit_size) - 1
            return value & mask
        elif var_type in ("int8", "int16", "int32", "int64", "int128", "int256"):
            bit_size = int(var_type[3:])
            return self.signed_wrap(value, bit_size)
        elif var_type in ("isize", "ptrdiff"):
            return self.signed_wrap(value, 64)
        elif var_type == "usize":
            return value % (1 << 64)
        return value

    def signed_wrap(self, value, bits):
        """Two's complement wrapping for signed integers"""
        return ((value + (1 << (bits - 1))) % (1 << bits)) - (1 << (bits - 1))

# ===== Interpreter =====

class Interpreter:
    """Enhanced interpreter with better error handling and features"""
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self.setup_builtins()

    def setup_builtins(self):
        """Setup built-in functions and constants"""
        # Built-in functions
        self.global_env.define("len", lambda x: len(x), is_const=True)
        self.global_env.define("range", lambda *args: list(range(*args)), is_const=True)
        self.global_env.define("str", lambda x: str(x), is_const=True)
        self.global_env.define("int", lambda x: int(x), is_const=True)
        self.global_env.define("float", lambda x: float(x), is_const=True)
        self.global_env.define("type", lambda x: type(x).__name__, is_const=True)
        
        # Math functions
        self.global_env.define("abs", abs, is_const=True)
        self.global_env.define("min", min, is_const=True)
        self.global_env.define("max", max, is_const=True)
        self.global_env.define("sum", sum, is_const=True)

    def eval(self, node):
        """Evaluate an AST node"""
        try:
            return self._eval_node(node)
        except (ReturnException, BreakException, ContinueException):
            # Re-raise control flow exceptions
            raise
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Runtime error: {e}", node)

    def _eval_node(self, node):
        """Internal evaluation dispatch"""
        
        # ===== Program =====
        if isinstance(node, Program):
            result = None
            for stmt in node.statements:
                result = self.eval(stmt)
            return result

        # ===== Variables =====
        elif isinstance(node, VarDecl):
            value = self.eval(node.value)
            self.env.define(node.name, value, node.var_type, node.is_const, node.is_mut)
            return value

        elif isinstance(node, Assignment):
            value = self.eval(node.value)
            if isinstance(node.name, MemberAccess):
                # obj.field = value
                obj = self.eval(node.name.obj)
                if isinstance(obj, Struct):
                    obj.fields[node.name.member] = value
                elif isinstance(obj, dict):
                    obj[node.name.member] = value
                else:
                    raise RuntimeError(f"Cannot assign to member of {type(obj).__name__}")
            else:
                self.env.set(node.name, value)
            return value

        elif isinstance(node, AugmentedAssignment):
            current = self.env.get(node.name)
            new_val = self.apply_augmented_op(current, node.operator, self.eval(node.value))
            self.env.set(node.name, new_val)
            return new_val

        elif isinstance(node, Identifier):
            return self.env.get(node.name)

        # ===== Literals =====
        elif isinstance(node, Literal):
            return node.value
        
        elif isinstance(node, ArrayLiteral):
            return [self.eval(elem) for elem in node.elements]
        
        elif isinstance(node, NullLiteral):
            return None
        
        elif isinstance(node, DictLiteral):
            return {self.eval(k): self.eval(v) for k, v in node.pairs}
        
        elif isinstance(node, TupleLiteral):
            return tuple(self.eval(e) for e in node.elements)
        
        elif isinstance(node, SetLiteral):
            return set(self.eval(e) for e in node.elements)
        
        elif isinstance(node, CharLiteral):
            val = node.value
            if val.startswith("\\"):
                escapes = {"\\n": "\n", "\\t": "\t", "\\'": "'", "\\\\": "\\", "\\r": "\r", "\\0": "\0"}
                return escapes.get(val, val[1:])
            return val
        
        elif isinstance(node, BigIntLiteral):
            return node.value
        
        elif isinstance(node, DecimalLiteral):
            return node.value
        
        elif isinstance(node, RangeLiteral):
            start = self.eval(node.start)
            end = self.eval(node.end)
            return Range(start, end, node.inclusive)
        
        elif isinstance(node, StringInterpolation):
            # Simplified - just return the parts concatenated
            return ''.join(str(self.eval(part)) for part in node.parts)

        # ===== Integer Types =====
        elif isinstance(node, UIntLiteral):
            val = self.eval(node.value)
            mask = (1 << node.bit_size) - 1
            return val & mask
        
        elif isinstance(node, IntLiteral):
            val = node.value
            if isinstance(val, Node):
                val = self.eval(val)
            return self.env.signed_wrap(val, node.bits)
        
        elif isinstance(node, SizeIntLiteral):
            val = self.eval(node.expr)
            if node.signed:
                return self.env.signed_wrap(val, 64)
            else:
                return val % (1 << 64)
        
        elif isinstance(node, PtrDiffLiteral):
            val = self.eval(node.expr)
            return self.env.signed_wrap(val, 64)

        # ===== Operators =====
        elif isinstance(node, BinaryOp):
            return self.eval_binary_op(node)
        
        elif isinstance(node, UnaryOp):
            return self.eval_unary_op(node)
        
        elif isinstance(node, TernaryOp):
            condition = self.eval(node.condition)
            if condition:
                return self.eval(node.true_val)
            else:
                return self.eval(node.false_val)

        # ===== Control Flow =====
        elif isinstance(node, IfStatement):
            if self.eval(node.condition):
                for stmt in node.then_body:
                    self.eval(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.eval(stmt)

        elif isinstance(node, WhileLoop):
            try:
                while self.eval(node.condition):
                    try:
                        for stmt in node.body:
                            self.eval(stmt)
                    except ContinueException:
                        continue
            except BreakException as e:
                pass

        elif isinstance(node, ForLoop):
            self.eval(node.init)
            try:
                while self.eval(node.condition):
                    try:
                        for stmt in node.body:
                            self.eval(stmt)
                    except ContinueException:
                        pass
                    self.eval(node.update)
            except BreakException:
                pass

        elif isinstance(node, ForInLoop):
            iterable = self.eval(node.iterable)
            
            # Handle Range objects
            if isinstance(iterable, Range):
                iterable = list(iterable)
            
            if not hasattr(iterable, "__iter__"):
                raise RuntimeError("Value in 'for ... in' is not iterable")
            
            try:
                for val in iterable:
                    self.env.define(node.var_name, val)
                    try:
                        for stmt in node.body:
                            self.eval(stmt)
                    except ContinueException:
                        continue
            except BreakException:
                pass

        elif isinstance(node, SwitchStatement):
            switch_val = self.eval(node.expr)
            executed = False
            for case_val, stmts in node.cases:
                if switch_val == self.eval(case_val):
                    try:
                        for stmt in stmts:
                            if isinstance(stmt, BreakStatement):
                                executed = True
                                break
                            if isinstance(stmt, ContinueStatement):
                                continue
                            self.eval(stmt)
                    except BreakException:
                        pass
                    executed = True
                    break
            if not executed and node.default:
                for stmt in node.default:
                    self.eval(stmt)

        elif isinstance(node, MatchStatement):
            value = self.eval(node.expr)
            for pattern, guard, body in node.arms:
                if self.match_pattern(pattern, value):
                    if guard is None or self.eval(guard):
                        for stmt in body:
                            self.eval(stmt)
                        break

        elif isinstance(node, BreakStatement):
            value = self.eval(node.value) if node.value else None
            raise BreakException(value)
        
        elif isinstance(node, ContinueStatement):
            raise ContinueException()
        
        elif isinstance(node, ReturnStatement):
            value = self.eval(node.expr) if node.expr else None
            raise ReturnException(value)

        # ===== Functions =====
        elif isinstance(node, FunctionDef):
            func = Function(node, self.env)
            self.env.define(node.name, func, is_const=True)
            return func

        elif isinstance(node, FunctionCall):
            return self.eval_function_call(node)

        elif isinstance(node, LambdaExpr):
            return Lambda(node.params, node.body, self.env)

        elif isinstance(node, YieldStatement):
            # Simplified generator support
            value = self.eval(node.expr)
            return value

        elif isinstance(node, AwaitExpr):
            # Simplified async support
            return self.eval(node.expr)

        # ===== I/O =====
        elif isinstance(node, PrintStatement):
            value = self.eval(node.expr)
            # Handle escape sequences in strings
            if isinstance(value, str):
                value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\\\', '\\')
            print(value)

        elif isinstance(node, PrintfStatement):
            fmt = self.eval(node.format_expr)
            values = [self.eval(arg) for arg in node.args]
            # Handle escape sequences properly
            fmt = fmt.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\\\', '\\')
            print(fmt % tuple(values), end="")

        # ===== Error Handling =====
        elif isinstance(node, TryCatchStatement):
            try:
                for stmt in node.try_block:
                    self.eval(stmt)
            except Exception as e:
                # Try each catch clause
                caught = False
                for exception_type, catch_var, catch_block in node.catch_clauses:
                    # Simple exception matching (can be enhanced)
                    if exception_type is None or exception_type in str(type(e).__name__):
                        if catch_var:
                            self.env.define(catch_var, str(e))
                        for stmt in catch_block:
                            self.eval(stmt)
                        caught = True
                        break
                if not caught:
                    raise
            finally:
                if node.finally_block:
                    for stmt in node.finally_block:
                        self.eval(stmt)

        elif isinstance(node, ThrowStatement):
            value = self.eval(node.expr)
            raise Exception(str(value))

        # ===== Data Structures =====
        elif isinstance(node, StructDef):
            self.env.structs[node.name] = node
            return None
        
        elif isinstance(node, TypedefStruct):
            self.env.structs[node.name] = node
            return None
        
        elif isinstance(node, UnionDef):
            # Store union definition - make sure unions dict exists
            self.env.unions[node.name] = node
            return None
        
        elif isinstance(node, TypedefUnion):
            # Store typedef union definition - make sure unions dict exists
            self.env.unions[node.name] = node
            return None
        
        elif isinstance(node, StructLiteral):
            # FIRST check if it's a union before checking struct
            current_env = self.env
            while current_env:
                if node.struct_name in current_env.unions:
                    # It's a union! Create Union object
                    union_def = current_env.unions[node.struct_name]
                    # Union can only have one field set
                    if isinstance(node.fields, dict) and len(node.fields) == 1:
                        field_name, value_expr = list(node.fields.items())[0]
                        return Union(node.struct_name, field_name, self.eval(value_expr))
                    else:
                        raise RuntimeError(f"Union '{node.struct_name}' can only be initialized with one field")
                current_env = current_env.parent
            
            # Not a union, check if it's a struct
            current_env = self.env
            struct_def = None
            while current_env:
                if node.struct_name in current_env.structs:
                    struct_def = current_env.structs[node.struct_name]
                    break
                current_env = current_env.parent
            
            if struct_def:
                fields = {}
                
                # First, apply all default values
                for field_info in struct_def.fields:
                    if len(field_info) == 3:  # Regular field
                        field_name, field_type, default_value = field_info
                        if default_value is not None:
                            fields[field_name] = self.eval(default_value)
                    elif len(field_info) == 2 and field_info[0] == "__union__":
                        # Anonymous union - don't set defaults
                        pass
                
                # Then, override with provided values
                if isinstance(node.fields, dict):
                    for name, value_expr in node.fields.items():
                        fields[name] = self.eval(value_expr)
                else:
                    # Positional initialization
                    for i, value_expr in enumerate(node.fields):
                        field_name = struct_def.fields[i][0]
                        fields[field_name] = self.eval(value_expr)
                
                return Struct(node.struct_name, fields)
            else:
                raise RuntimeError(f"Undefined struct or union: {node.struct_name}")
                    
        elif isinstance(node, EnumDef):
            self.env.enums[node.name] = node
            # Create constructor functions for each variant
            for variant_name, _ in node.variants:
                def make_variant(enum_name, var_name):
                    def constructor(*args):
                        return Enum(enum_name, var_name, args if args else None)
                    return constructor
                self.env.define(f"{node.name}_{variant_name}", 
                                make_variant(node.name, variant_name), 
                                is_const=True)
            return None
        
        elif isinstance(node, TypeAlias):
            self.env.types[node.name] = node.type_expr
            return None
        
        # ===== Member Access =====
        elif isinstance(node, IndexAccess):
            collection = self.eval(node.collection)
            index = self.eval(node.index)
            try:
                return collection[index]
            except (KeyError, IndexError, TypeError) as e:
                raise RuntimeError(f"Cannot index {type(collection).__name__} with {index}: {e}")

        elif isinstance(node, MemberAccess):
            obj = self.eval(node.obj)
            if isinstance(obj, Struct):
                if node.member in obj.fields:
                    return obj.fields[node.member]
                raise RuntimeError(f"Struct {obj.struct_name} has no field '{node.member}'")
            elif isinstance(obj, Union):
                # For unions, you can only access the active field
                if node.member == obj.active_field:
                    return obj.value
                else:
                    raise RuntimeError(f"Union field '{node.member}' is not active (active field is '{obj.active_field}')")
            elif isinstance(obj, dict):
                return obj.get(node.member)
            else:
                raise RuntimeError(f"Cannot access member '{node.member}' of {type(obj).__name__}")
        
        elif isinstance(node, SliceAccess):
            collection = self.eval(node.collection)
            start = self.eval(node.start) if node.start else None
            end = self.eval(node.end) if node.end else None
            step = self.eval(node.step) if node.step else None
            return collection[start:end:step]
        
        # ===== Imports =====
        elif isinstance(node, ImportStatement):
            # Simplified - just acknowledge the import
            return None
        
        else:
            raise RuntimeError(f"Unknown node type: {type(node).__name__}")
        
    def eval_binary_op(self, node):
        """Evaluate binary operators"""
        left = self.eval(node.left)
        right = self.eval(node.right)
        op = node.op

        # Set operations
        if isinstance(left, set) or isinstance(right, set):
            if op == '+':
                return set(left).union(right)
            elif op == '*':
                return set(left).intersection(right)
            elif op == '-':
                return set(left).difference(right)
            elif op == 'in':
                return left in right

        # Arithmetic
        if op == "+":
            return left + right
        elif op == "-":
            return left - right
        elif op == "*":
            return left * right
        elif op == "/":
            return left / right
        elif op == "//":
            return left // right
        elif op == "%":
            return left % right
        elif op == "**":
            return left ** right

        # Comparison
        elif op == "==":
            return left == right
        elif op == "!=":
            return left != right
        elif op == "<":
            return left < right
        elif op == ">":
            return left > right
        elif op == "<=":
            return left <= right
        elif op == ">=":
            return left >= right
        elif op == "===":
            return left is right
        elif op == "!==":
            return left is not right
        elif op == "<=>":
            return -1 if left < right else (0 if left == right else 1)
        elif op == "in":
            return left in right

        # Logical
        elif op == "and" or op == "&&":
            return left and right
        elif op == "or" or op == "||":
            return left or right
        elif op == "xor":
            return bool(left) ^ bool(right)
        elif op == "then":
            return (not left) or right
        elif op == "nand":
            return not (left and right)

        # Bitwise
        elif op == "&":
            return int(left) & int(right)
        elif op == "|":
            return int(left) | int(right)
        elif op == "^":
            return int(left) ^ int(right)
        elif op == "<<":
            return int(left) << int(right)
        elif op == ">>":
            return int(left) >> int(right)

        else:
            raise RuntimeError(f"Unknown binary operator: {op}")

    def eval_unary_op(self, node):
        """Evaluate unary operators"""
        val = self.eval(node.expr)
        op = node.op

        if op == "not" or op == "!":
            return not val
        elif op == "+":
            return +val
        elif op == "-":
            return -val
        elif op == "~":
            return ~int(val)
        elif op == "++":
            # Pre-increment
            if isinstance(node.expr, Identifier):
                new_val = val + 1
                self.env.set(node.expr.name, new_val)
                return new_val
            raise RuntimeError("Cannot increment non-variable")
        elif op == "--":
            # Pre-decrement
            if isinstance(node.expr, Identifier):
                new_val = val - 1
                self.env.set(node.expr.name, new_val)
                return new_val
            raise RuntimeError("Cannot decrement non-variable")
        elif op == "++_post":
            # Post-increment
            if isinstance(node.expr, Identifier):
                self.env.set(node.expr.name, val + 1)
                return val
            raise RuntimeError("Cannot increment non-variable")
        elif op == "--_post":
            # Post-decrement
            if isinstance(node.expr, Identifier):
                self.env.set(node.expr.name, val - 1)
                return val
            raise RuntimeError("Cannot decrement non-variable")
        else:
            raise RuntimeError(f"Unknown unary operator: {op}")

    def apply_augmented_op(self, left, op, right):
        """Apply augmented assignment operator"""
        ops = {
            "+=": operator.add,
            "-=": operator.sub,
            "*=": operator.mul,
            "/=": operator.truediv,
            "//=": operator.floordiv,
            "%=": operator.mod,
            "**=": operator.pow,
            "&=": operator.and_,
            "|=": operator.or_,
            "^=": operator.xor,
            "<<=": operator.lshift,
            ">>=": operator.rshift,
        }
        if op in ops:
            return ops[op](left, right)
        raise RuntimeError(f"Unknown augmented operator: {op}")

    def eval_function_call(self, node):
        """Evaluate function call"""
        func = self.eval(node.name) if isinstance(node.name, Node) else self.env.get(node.name)
        
        # Built-in Python callable
        if callable(func) and not isinstance(func, (Function, Lambda)):
            args = [self.eval(arg) for arg in node.args]
            return func(*args)
        
        # User-defined function
        elif isinstance(func, Function):
            # Check argument count with default parameters
            required_params = sum(1 for _, _, default in func.def_node.params if default is None)
            total_params = len(func.def_node.params)
            provided_args = len(node.args)
            
            if provided_args < required_params or provided_args > total_params:
                raise RuntimeError(f"Function '{func.def_node.name}' expects {required_params}-{total_params} arguments, got {provided_args}")
            
            # Create new environment for function
            func_env = Environment(parent=func.env)
            
            # Bind parameters with provided arguments and defaults
            for i, (param_type, param_name, default) in enumerate(func.def_node.params):
                if i < len(node.args):
                    # Use provided argument
                    value = self.eval(node.args[i])
                else:
                    # Use default value
                    value = self.eval(default) if default else None
                func_env.define(param_name, value, param_type)
            
            # Handle kwargs
            if hasattr(node, 'kwargs') and node.kwargs:
                for name, value_expr in node.kwargs.items():
                    value = self.eval(value_expr)
                    func_env.set(name, value)
            
            # Execute function body
            prev_env = self.env
            self.env = func_env
            
            try:
                for stmt in func.def_node.body:
                    self.eval(stmt)
                return None
            except ReturnException as e:
                return e.value
            finally:
                self.env = prev_env
        
        # Lambda
        elif isinstance(func, Lambda):
            if len(node.args) != len(func.params):
                raise RuntimeError(f"Lambda expects {len(func.params)} arguments, got {len(node.args)}")
            
            lambda_env = Environment(parent=func.env)
            for param, arg in zip(func.params, node.args):
                value = self.eval(arg)
                lambda_env.define(param, value)
            
            prev_env = self.env
            self.env = lambda_env
            result = self.eval(func.body)
            self.env = prev_env
            return result
        
        else:
            raise RuntimeError(f"'{node.name}' is not callable")

    def match_pattern(self, pattern, value):
        """Match a pattern against a value"""
        # Wildcard
        if isinstance(pattern, Identifier) and pattern.name == "_":
            return True
        
        # Literal match
        if isinstance(pattern, Literal):
            return pattern.value == value
        
        # Variable binding (always matches)
        if isinstance(pattern, Identifier):
            self.env.define(pattern.name, value)
            return True
        
        # Tuple pattern
        if isinstance(pattern, TupleLiteral):
            if not isinstance(value, tuple) or len(pattern.elements) != len(value):
                return False
            return all(self.match_pattern(p, v) for p, v in zip(pattern.elements, value))
        
        # Array pattern
        if isinstance(pattern, ArrayLiteral):
            if not isinstance(value, list) or len(pattern.elements) != len(value):
                return False
            return all(self.match_pattern(p, v) for p, v in zip(pattern.elements, value))
        
        # Enum variant match
        if isinstance(pattern, StructLiteral):
            if isinstance(value, Enum):
                return value.variant_name == pattern.struct_name
        
        return False