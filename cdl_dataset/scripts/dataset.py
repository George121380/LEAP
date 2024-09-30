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
                data['Actions'] = line.partition(':')[2].strip().replace(' ','').split(';')
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

if __name__ == '__main__':
    data = parse_file_to_json('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Change_TV_channel/g2.txt')
    print(data)