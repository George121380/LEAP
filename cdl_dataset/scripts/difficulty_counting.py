import csv
from collections import defaultdict
import re
import json

def parse_csv(file_path):
    result = defaultdict(dict)
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
        for row in reader:
            task_path = row['Goal Representation'].strip()
            kn = row['Debug Result'].strip()
            missed_action_info = row['Add Info'].strip()
            match = re.search(r'missed action num:\s*(\d+)', missed_action_info)
            if match:
                missed_action_num = int(match.group(1))
                if missed_action_num==0:
                    continue
                result[task_path][kn] = missed_action_num
    return result

if __name__=='__main__':
    file_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/log/epoch_20241014_060537/epoch.csv'
    result = parse_csv(file_path)
    print(result)
    json_output_path = 'cdl_dataset/difficulty_counting.json'
    with open(json_output_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(result, jsonfile, ensure_ascii=False, indent=4)