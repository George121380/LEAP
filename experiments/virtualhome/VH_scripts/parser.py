import re

class ASTNode:
    pass

class PredicateNode(ASTNode):
    def __init__(self, name):
        self.name = name

class ThenNode(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class OrNode(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

def tokenize(expression):
    tokens = re.findall(r'\s*(then|or|\(|\)|k\d+)\s*', expression)
    return tokens

def parse(tokens):
    def parse_expression(index):
        node, index = parse_term(index)
        while index < len(tokens) and tokens[index] == 'or':
            index += 1
            right_node, index = parse_term(index)
            node = OrNode(node, right_node)
        return node, index

    def parse_term(index):
        node, index = parse_factor(index)
        while index < len(tokens) and tokens[index] == 'then':
            index += 1
            right_node, index = parse_factor(index)
            node = ThenNode(node, right_node)
        return node, index

    def parse_factor(index):
        token = tokens[index]
        if token == '(':
            index += 1
            node, index = parse_expression(index)
            if tokens[index] != ')':
                raise SyntaxError('Expected )')
            index += 1
            return node, index
        elif re.match(r'k\d+', token):
            node = PredicateNode(token)
            index += 1
            return node, index
        else:
            raise SyntaxError(f'Unexpected token: {token}')

    ast, index = parse_expression(0)
    if index != len(tokens):
        raise SyntaxError('Unexpected tokens at the end')
    return ast

def evaluate(ast, context):
    if isinstance(ast, PredicateNode):
        return context[ast.name]()
    elif isinstance(ast, ThenNode):
        return evaluate(ast.left, context) and evaluate(ast.right, context)
    elif isinstance(ast, OrNode):
        return evaluate(ast.left, context) or evaluate(ast.right, context)
    else:
        raise ValueError('Unknown AST node')

def k1():
    print("Evaluating k1")
    return False

def k2():
    print("Evaluating k2")
    return False

def k3():
    print("Evaluating k3")
    return True

def k4():
    print("Evaluating k4")
    return True

def k5():
    print("Evaluating k5")
    return False

# 主函数
if __name__ == "__main__":
    expression = "(k1 then k2 then k3) or (k2 then (k4 or k5))"
    tokens = tokenize(expression)
    ast = parse(tokens)
    context = {'k1': k1, 'k2': k2, 'k3': k3, 'k4': k4, 'k5': k5}
    result = evaluate(ast, context)
    print(f"The result of the expression is {result}")
