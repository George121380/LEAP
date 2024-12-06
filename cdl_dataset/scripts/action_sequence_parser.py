import re

# This file is used to parse required actions and return the possible combinations of the actions.

class Expr:
    pass

class Action(Expr):
    def __init__(self, action):
        self.action = action

    def __repr__(self):
        return f"Action({self.action})"

class OrExpr(Expr):
    def __init__(self, options):
        self.options = options

    def __repr__(self):
        return f"OrExpr({self.options})"

class ThenExpr(Expr):
    def __init__(self, steps):
        self.steps = steps

    def __repr__(self):
        return f"ThenExpr({self.steps})"

def action_tokenize(s):
    pattern = r'\(|\)|or|then|[a-zA-Z_]\w*\([^\)]*\)'
    tokens = re.findall(pattern, s)
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.length = len(tokens)

    def parse(self):
        return self.parse_expr()

    def current_token(self):
        if self.pos < self.length:
            return self.tokens[self.pos]
        else:
            return None

    def consume(self, expected_token=None):
        token = self.current_token()
        if expected_token and token != expected_token:
            raise Exception(f"Expected token {expected_token}, got {token}")
        self.pos += 1
        return token

    def parse_expr(self):
        return self.parse_then_expr()

    def parse_then_expr(self):
        left = self.parse_or_expr()
        tokens = [left]
        while self.current_token() == 'then':
            self.consume('then')
            right = self.parse_or_expr()
            tokens.append(right)
        if len(tokens) == 1:
            return tokens[0]
        else:
            return ThenExpr(tokens)

    def parse_or_expr(self):
        left = self.parse_factor()
        options = [left]
        while self.current_token() == 'or':
            self.consume('or')
            right = self.parse_factor()
            options.append(right)
        if len(options) == 1:
            return options[0]
        else:
            return OrExpr(options)

    def parse_factor(self):
        token = self.current_token()
        if token == '(':
            self.consume('(')
            expr = self.parse_expr()
            self.consume(')')
            return expr
        elif re.match(r'[a-zA-Z_]\w*\([^\)]*\)', token):
            action = self.consume()
            return Action(action)
        else:
            raise Exception(f"Unexpected token {token}")

def generate_sequences(expr):
    if isinstance(expr, Action):
        return [[expr.action]]
    elif isinstance(expr, OrExpr):
        sequences = []
        for option in expr.options:
            sequences.extend(generate_sequences(option))
        return sequences
    elif isinstance(expr, ThenExpr):
        sequences = [[]]
        for step in expr.steps:
            step_sequences = generate_sequences(step)
            new_sequences = []
            for seq in sequences:
                for step_seq in step_sequences:
                    new_sequences.append(seq + step_seq)
            sequences = new_sequences
        return sequences
    else:
        raise Exception(f"Unknown expression type: {expr}")

def is_subsequence(needle, haystack):
    needle_len = len(needle)
    haystack_len = len(haystack)
    i = 0
    for action in haystack:
        if action['action'] == needle[i]:
            i += 1
            if i == needle_len:
                return True
    return False

def parse_action_sequence_from_file_path(file_path,scene_id):
    """
    This is the only function that should be called from outside
    
    Input : The path to the file
    Output : A list of possible action sequences
    """
    # Read the file and ensure it only contains one line starting with "Actions"
    actions_defination=None
    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith(f"S{scene_id}_Actions"):
                actions_defination=line
                break
    if actions_defination is None:
        return []
    tokens = action_tokenize(actions_defination)
    parser = Parser(tokens)
    expr = parser.parse()
    sequences = generate_sequences(expr)
    return sequences


if __name__ == "__main__":
    task_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Clean_the_bathroom/g2.txt'
    sequences = parse_action_sequence_from_file_path(task_path)
    print(sequences)