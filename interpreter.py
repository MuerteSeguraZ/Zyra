from ast_nodes import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class Function:
    def __init__(self, def_node, env):
        self.def_node = def_node
        self.env = env

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise Exception(f"Variable '{name}' not defined")

    def set(self, name, value):
        self.vars[name] = value

class Interpreter:
    def __init__(self):
        self.env = Environment()

    def eval(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.eval(stmt)

        elif isinstance(node, VarDecl):
            self.env.set(node.name, self.eval(node.value))

        elif isinstance(node, Assignment):
            self.env.set(node.name, self.eval(node.value))

        elif isinstance(node, Identifier):
            return self.env.get(node.name)

        elif isinstance(node, Literal):
            return node.value

        elif isinstance(node, PrintStatement):
            value = self.eval(node.expr)
            print(value)

        elif isinstance(node, BinaryOp):
            left = self.eval(node.left)
            right = self.eval(node.right)

            if node.op == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if node.op == "-": return left - right
            if node.op == "*": return left * right
            if node.op == "/": return left / right  # always float division
            if node.op == "==": return left == right
            if node.op == "<": return left < right
            if node.op == ">": return left > right
            if node.op == "<=": return left <= right
            if node.op == ">=": return left >= right

            # --- Logical operators ---
            if node.op == "and": return bool(left) and bool(right)
            if node.op == "or": return bool(left) or bool(right)
            if node.op == "xor": return bool(left) ^ bool(right)
            if node.op == "then": 
                # logical implication: A → B is equivalent to (not A) or B
                return (not bool(left)) or bool(right)
            if node.op == "nand":
                return not (bool(left) and bool(right))

            raise Exception(f"Unknown operator {node.op}")
        
        elif isinstance(node, UnaryOp):
            val = self.eval(node.expr)
            if node.op == "not":
                return not val
            else:
                raise Exception(f"Unknown unary operator {node.op}")
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
            except BreakException:
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
            
        elif isinstance(node, SwitchStatement):
            switch_val = self.eval(node.expr)
            executed = False
            for case_val, stmts in node.cases:
                if switch_val == self.eval(case_val):
                    for stmt in stmts:
                        if isinstance(stmt, BreakStatement):
                            executed = True
                            break
                        if isinstance(stmt, ContinueStatement):
                            continue
                        self.eval(stmt)
                    executed = True
                    break
            if not executed and node.default:
                for stmt in node.default:
                    self.eval(stmt)
            
        elif isinstance(node, BreakStatement):
            raise BreakException()
        
        elif isinstance(node, ContinueStatement):
            raise ContinueException()

        elif isinstance(node, FunctionDef):
            self.env.set(node.name, Function(node, self.env))

        elif isinstance(node, FunctionCall):
            return self.eval_function_call(node)

        elif isinstance(node, ReturnStatement):
            raise ReturnException(self.eval(node.expr))

        else:
            raise Exception(f"Unknown node type: {node}")

    def eval_function_call(self, node):
        func = self.env.get(node.name)
        if not isinstance(func, Function):
            raise Exception(f"'{node.name}' is not a function")
        if len(node.args) != len(func.def_node.params):
            raise Exception("Argument count mismatch")

        new_env = Environment(parent=func.env)
        for (typ, name), arg in zip(func.def_node.params, node.args):
            new_env.set(name, self.eval(arg))

        prev_env = self.env
        self.env = new_env

        try:
            for stmt in func.def_node.body:
                self.eval(stmt)
        except ReturnException as e:
            ret_val = e.value
        else:
            ret_val = None

        self.env = prev_env
        return ret_val
