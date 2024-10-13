import pandas as pd
import re

def parse_completion_rates(csv_file_path):
    df = pd.read_csv(csv_file_path)
    result_list = []

    for index, row in df.iterrows():
        completion_rate = row['LLM Answer'] 
        task_path = row['Plan']

        if completion_rate=='1':
            result_dict = {
            'task_path': task_path,
            'keystate_completion_rate': True,
            'action_completion_rate': True,
            'success': True
        }


        keystate_matches = re.findall(r'(Keystate: k\d+) - Completion Rate: ([\d.]+)', completion_rate)
        action_match = re.search(r'Action Completion Rate: ([\d.]+|No actions required)', completion_rate)

        keystate_dict = {}
        for keystate, completion_rate in keystate_matches:
            keystate_dict[keystate] = float(completion_rate)

        if action_match and action_match.group(1) != 'No actions required':
            action_completion_rate = float(action_match.group(1))
        else:
            action_completion_rate = 0.0 

        result_dict = {
            'task_path': task_path,
            'keystate_completion_rate': keystate_dict,
            'action_completion_rate': action_completion_rate,
            'success': False
        }

        result_list.append(result_dict)

    return result_list

csv_file_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/log/Ours_o_human/epoch.csv'
result = parse_completion_rates(csv_file_path)

# 打印结果
for entry in result:
    print(entry)
