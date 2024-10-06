import os
import json
import re

def split_task_description():
    # Split task description(discription.json) into individual files (in dataset folder)
    task_description_file='cdl_dataset/discription.json'
    dataset_folder='cdl_dataset/dataset'
    with open(task_description_file) as f:
        task_description=json.load(f)
    task_description=task_description['scene_1']
    for task in task_description:
        os.mkdir(os.path.join(dataset_folder,task['task_name'].replace(' ','_')))
        for goal in task['goals']:
            file_path=os.path.join(dataset_folder,task['task_name'].replace(' ','_'),goal+".txt")
            file = open(file_path, 'w', newline='', encoding='utf-8')
            file.write("Task name: "+task['task_name'])
            file.write('\n')
            file.write("Goal: "+task['goals'][goal])

def parse_file_to_json(file_path):
    # Parse a task.txt into a operatable json format
    data = {}
    behaviors = {}
    current_behavior_name = None
    behavior_content = ''
    in_behavior = False

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    index = 0
    while index < len(lines):
        line = lines[index].rstrip('\n')

        if not in_behavior:
            # Parse the initial sections: Task name, Goal, Logic
            if line.startswith('Task name:'):
                data['Task name'] = line.partition(':')[2].strip()
            elif line.startswith('Goal:'):
                data['Goal'] = line.partition(':')[2].strip()
            elif line.startswith('Logic:'):
                data['Logic'] = line.partition(':')[2].strip()
            elif line.startswith('Actions'):
                data['Actions'] = line.partition(':')[2]
            elif line.startswith('behavior'):
                in_behavior = True
                # Extract behavior name using regex
                match = re.match(r'behavior (\w+)\(\):', line)
                if match:
                    current_behavior_name = match.group(1)
                    behavior_content = line + '\n'
                else:
                    raise ValueError(f"Invalid behavior declaration: {line}")
            # Skip empty lines
        else:
            # Check if a new behavior starts
            if line.startswith('behavior') and re.match(r'behavior (\w+)\(\):', line):
                # Save the previous behavior
                behaviors[current_behavior_name] = behavior_content.rstrip('\n')
                # Start new behavior
                match = re.match(r'behavior (\w+)\(\):', line)
                current_behavior_name = match.group(1)
                behavior_content = line + '\n'
            else:
                behavior_content += line + '\n'
        index += 1

    # After the loop, save the last behavior
    if in_behavior and current_behavior_name:
        behaviors[current_behavior_name] = behavior_content.rstrip('\n')

    data['Keystates'] = behaviors
    return data

###############################################
#functions used to evaluate action sequences
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
        if action == needle[i]:
            i += 1
            if i == needle_len:
                return True
    return False

###############################################

if __name__ == '__main__':
    data = parse_file_to_json('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Change_TV_channel/g2.txt')
    print(data)