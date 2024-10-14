import re
from dataset import parse_file_to_json

class Token:
    def __init__(self, type, value):
        self.type = type  # 'IDENT', 'THEN', 'OR', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

def tokenize(s):
    token_specification = [
        ('THEN',   r'then'),
        ('OR',     r'or'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('IDENT',  r'[a-zA-Z_]\w*'),
        ('SKIP',   r'[ \t]+'),
        ('MISMATCH', r'.'),  # Any other character
    ]
    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    mo = get_token(s)
    tokens = []
    while mo is not None:
        typ = mo.lastgroup
        if typ == 'EOF':
            break
        elif typ == 'SKIP':
            pass
        elif typ == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {s[pos]} at position {pos}')
        else:
            val = mo.group(typ)
            tokens.append(Token(typ, val))
        pos = mo.end()
        mo = get_token(s, pos)
    tokens.append(Token('EOF', None))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def consume(self, expected_type=None):
        token = self.tokens[self.pos]
        if expected_type and token.type != expected_type:
            raise RuntimeError(f'Expected token {expected_type}, got {token.type}')
        self.pos += 1
        return token

    def parse(self):
        return self.expression()

    def expression(self):
        node = self.term()
        while self.tokens[self.pos].type == 'OR':
            self.consume('OR')
            right = self.term()
            node = ('OR', node, right)
        return node

    def term(self):
        node = self.factor()
        while self.tokens[self.pos].type == 'THEN':
            self.consume('THEN')
            right = self.factor()
            node = ('THEN', node, right)
        return node

    def factor(self):
        token = self.tokens[self.pos]
        if token.type == 'IDENT':
            self.consume('IDENT')
            return ('IDENT', token.value)
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.expression()
            self.consume('RPAREN')
            return node
        else:
            raise RuntimeError(f'Unexpected token {token.type}')

def evaluate(node):
    if node[0] == 'IDENT':
        return [[node[1]]]
    elif node[0] == 'THEN':
        left = evaluate(node[1])
        right = evaluate(node[2])
        result = []
        for l in left:
            for r in right:
                result.append(l + r)
        return result
    elif node[0] == 'OR':
        left = evaluate(node[1])
        right = evaluate(node[2])
        return left + right
    else:
        raise RuntimeError(f'Unknown node type {node[0]}')

def parse_logic(logic_str):
    tokens = tokenize(logic_str)
    parser = Parser(tokens)
    ast = parser.parse()
    combinations = evaluate(ast)
    return combinations

def parse_logic_from_file_path(file_path):
    with open(file_path, 'r') as f:
        logic_str = f.read()
    if 'Logic' not in parse_file_to_json(file_path):
        return "No keystate is needed"
    logic_str=parse_file_to_json(file_path)['Logic']
    combinations = parse_logic(logic_str)
    return combinations


if __name__ == '__main__':
    file_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Change_TV_channel/g2.txt'
    combination=parse_logic_from_file_path(file_path)
    for combo in combination:
        print('Combination:', combo)
    print()