from ast_nodes import *

class Environment:
    def __init__(self):
        self.vars = {}

class Interpreter:
    def __init__(self):
        self.env = Environment()

    def eval(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.eval(stmt)

        elif isinstance(node, VarDecl):
            self.env.vars[node.name] = self.eval(node.value)

        elif isinstance(node, Assignment):
            self.env.vars[node.name] = self.eval(node.value)

        elif isinstance(node, Identifier):
            return self.env.vars.get(node.name)

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
            if node.op == "/": return left / right
            if node.op == "==": return left == right
            if node.op == "<": return left < right
            if node.op == ">": return left > right
            if node.op == "<=": return left <= right
            if node.op == ">=": return left >= right
            raise Exception(f"Unknown operator {node.op}")

        elif isinstance(node, IfStatement):
            if self.eval(node.condition):
                for stmt in node.then_body:
                    self.eval(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.eval(stmt)

        elif isinstance(node, WhileLoop):
            while self.eval(node.condition):
                for stmt in node.body:
                    self.eval(stmt)

        elif isinstance(node, ForLoop):
            self.eval(node.init)
            while self.eval(node.condition):
                for stmt in node.body:
                    self.eval(stmt)
                self.eval(node.update)

        else:
            raise Exception(f"Unknown node type: {node}")
