import json
import sys
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.append('cdl_dataset/scripts')
from dataset import parse_file_to_json
from action_sequence_parser import parse_action_sequence_from_file_path

scene_id = 0

with open('cdl_dataset/scenes/diff_0.json', 'r') as file:
    data_0 = json.load(file)

with open('cdl_dataset/scenes/diff_1.json', 'r') as file:
    data_1 = json.load(file)

with open('cdl_dataset/scenes/diff_2.json', 'r') as file:
    data_2 = json.load(file)

task_lengths = {}

scene_id = 0
for data in [data_0, data_1, data_2]:
    for task, solutions in data.items():
        required_actions = None
        task_data = parse_file_to_json(task)
        action_sequences=parse_action_sequence_from_file_path(task,scene_id)
        action_seq_len_min = float('inf')
        for action_sequence in action_sequences:
            action_seq_len = len(action_sequence)
            if action_seq_len < action_seq_len_min:
                action_seq_len_min = action_seq_len
        min_length = float('inf')
        
        for solution, values in solutions.items():
            total_length = sum(values.values())
            
            if total_length < min_length:
                min_length = total_length

        if min_length == float('inf'):
            min_length = 0

        if action_seq_len_min == float('inf'):
            task_lengths[task+str(scene_id)] = min_length
        else:
            task_lengths[task+str(scene_id)] = min_length + action_seq_len_min*2
    scene_id += 1


for task, length in task_lengths.items():
    print(f"Task: {task}, Solution Length: {length}")

length_list = list(task_lengths.values())
# plt.hist(length_list, bins=50, edgecolor='black', alpha=0.75)
sns.kdeplot(length_list, shade=True, bw_adjust=0.5)
plt.xlabel('Action Length')
plt.ylabel('Frequency')
plt.title('Distribution of Action Lengths')
plt.grid(True)
plt.show()