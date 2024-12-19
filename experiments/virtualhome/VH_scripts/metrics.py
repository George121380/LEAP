import pandas as pd
import re
import sys
import json
import os
import matplotlib.pyplot as plt
from collections import defaultdict

sys.path.append('cdl_dataset/scripts')
from logic_parser import parse_logic_from_file_path


def parse_info(log_text):
    parsed_data = {}
    # Use regex to extract the relevant fields
    parsed_data['Time consume'] = int(re.search(r"Time consume: (\d+) seconds", log_text).group(1))
    parsed_data['Exp_helper query times'] = int(re.search(r"Exp_helper query times: (\d+)", log_text).group(1))
    parsed_data['Guidance query times'] = int(re.search(r"Guidance query times: (\d+)", log_text).group(1))
    parsed_data['library scale'] = re.search(r"library scale: ([\d']+)", log_text).group(1)
    return parsed_data


def calculate_moving_average(data_list, window_size):
    """
    计算滑动平均值。

    Args:
    - data_list (list): 数据列表。
    - window_size (int): 滑动窗口大小。

    Returns:
    - list: 滑动平均值列表。
    """
    
    moving_averages = []
    for i in range(len(data_list) - window_size + 1):
        window = data_list[i:i + window_size]
        moving_average = sum(window) / window_size
        moving_averages.append(moving_average)
    return moving_averages


def plot_moving_average(moving_averages, output_path, ylabel, title):
    """
    绘制滑动平均值曲线并保存。

    Args:
    - moving_averages (list): 滑动平均值列表。
    - output_path (str): 图像保存路径。
    - ylabel (str): Y轴标签。
    - title (str): 图表标题。
    """
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(moving_averages)), moving_averages, marker='o')
    plt.xlabel('Task Number')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def find_csv_files(root_dir):
    """
    从指定根目录中递归查找所有的`epoch.csv`文件。

    Args:
    - root_dir (str): 要搜索的根目录路径。

    Returns:
    - list: (实验名, csv文件路径) 的列表。
    """
    for root, dirs, files in os.walk(root_dir):
        if 'epoch.csv' in files:
            experiment_name = os.path.basename(root)
            csv_file_path = os.path.join(root, 'epoch.csv')
            return (experiment_name, csv_file_path)


def parse_completion_rates(csv_file_path):
    df = pd.read_csv(csv_file_path)
    result_list = []
    guidance_nums = []

    for index, row in df.iterrows():
        info = {'Guidance query times': 0}
        if row['Info'] == 'Info' or row['Task Category']=='Evaluation Finished':
            continue
        if row['Content'] != 'Syntax Error':
            info = parse_info(row['Info'])
        guidance_nums.append(info['Guidance query times']) 

        completion_rate = row['Success Rate']
        debug_result = row['Content']
        end_report = row['Task Category']
        scene_id = row['Task Path']
        match = re.search(r"Scene_id:\s*(\d+)", scene_id)
        scene_id = match.group(1) if match else None

        if completion_rate == '1':
            result_dict = {
                'task_path': end_report,
                'keystate_completion_rate': True,
                'action_completion_rate': True,
                'success': True,
                'guidance_num': info['Guidance query times'],
                'Scene_id': scene_id,
            }
            result_list.append(result_dict)
            continue

        if debug_result == 'Syntax Error':
            result_dict = {
                'task_path': end_report,
                'keystate_completion_rate': False,
                'action_completion_rate': False,
                'success': 'syntax error',
                'guidance_num': info['Guidance query times'],
                'Scene_id': scene_id,
            }
            result_list.append(result_dict)
            continue

        if end_report == 'Evaluation Finished':
            continue

        keystate_matches = re.findall(r'(Keystate: k\d+) - Requires: ([\d.]+)', completion_rate)
        action_match = re.search(r'Action Completion Rate: ([\d.]+|No actions required)', completion_rate)

        keystate_dict = {}
        for keystate, rate in keystate_matches:
            keystate_dict[keystate.replace('Keystate: ', '')] = float(rate)

        if action_match and action_match.group(1) != 'No actions required':
            action_completion_rate = float(action_match.group(1))
        else:
            action_completion_rate = 'No actions required'

        result_dict = {
            'task_path': end_report,
            'keystate_completion_rate': keystate_dict,
            'action_completion_rate': action_completion_rate,
            'success': False,
            'guidance_num': info['Guidance query times'],
            'Scene_id': scene_id,
        }

        result_list.append(result_dict)

    return result_list, guidance_nums


def calculation(result_list):
    diff_0 = json.load(open('cdl_dataset/scenes/diff_0.json'))
    diff_1 = json.load(open('cdl_dataset/scenes/diff_1.json'))
    diff_2 = json.load(open('cdl_dataset/scenes/diff_2.json'))
    difficulty_dict = {'scene_0': diff_0, 'scene_1': diff_1, 'scene_2': diff_2}
    success_rate_list = []
    sum_success_rate = 0
    for entry in result_list:
        task_success_rate = 0
        task_path = entry['task_path']
        scene_id = entry['Scene_id']

        if entry['success'] == 'syntax error':
            task_success_rate = 0
        elif entry['success']:
            task_success_rate = 1
        else:
            solution_combination = parse_logic_from_file_path(task_path)
            if solution_combination == 'No keystate is needed':
                task_success_rate = entry['action_completion_rate']
            else:
                max_keystate_completion_rate = 0
                for solution in solution_combination:
                    solution_steps_num = 0
                    current_solution_keystate_completion_rate = 0
                    for keystate in solution:
                        keystate_steps_num = difficulty_dict[f'scene_{scene_id}'][task_path][str(solution)][keystate]
                        solution_steps_num += keystate_steps_num
                        if not keystate in entry['keystate_completion_rate']:
                            steps_left = keystate_steps_num
                        else:
                            steps_left = entry['keystate_completion_rate'][keystate]
                        current_solution_keystate_completion_rate += steps_left

                    current_solution_keystate_completion_rate = (solution_steps_num - current_solution_keystate_completion_rate) / solution_steps_num
                    max_keystate_completion_rate = max(max_keystate_completion_rate, current_solution_keystate_completion_rate)

                if entry['action_completion_rate'] == 'No actions required':
                    task_success_rate = max_keystate_completion_rate
                else:
                    keystate_weight = 2
                    action_weight = 1
                    task_success_rate = (max_keystate_completion_rate * keystate_weight + entry['action_completion_rate'] * action_weight) / (keystate_weight + action_weight)

        success_rate_list.append({"task":task_path,"suc_rate":round(task_success_rate, 3)})
        sum_success_rate += task_success_rate

    avg_success_rate = sum_success_rate / len(success_rate_list)
    return avg_success_rate, success_rate_list

def find_tasks_with_declining_success(tasks):
    task_groups = defaultdict(list)
    
    for task in tasks:
        task_groups[task["task"]].append(task["suc_rate"])
    
    declining_tasks = []
    scores = {}
    
    for task_name, rates in task_groups.items():
        if len(rates) != 3:
            continue
        
        first, second, third = rates[0], rates[1], rates[2]
        # if second < first or first > third or (first==second and first==third and first!=1):
        #     declining_tasks.append(task_name)
        #     scores.update({f"{task_name}":(first, second, third)})

        if second == 1 and first == 1 and third ==1:
            declining_tasks.append(task_name)
            scores.update({f"{task_name}":(first, second, third)})
            
    return declining_tasks, scores

if __name__ == '__main__':
    # methods_experiments = find_csv_files('log/main_with_guidance')
    methods_experiments=[]

    methods_experiments.append(find_csv_files('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/main_results/LLM+P_without_guidance'))

    # methods_experiments.append(find_csv_files('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/main_results/ours_without_guidance_1207'))

    # methods_experiments.append(find_csv_files('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/main_results/ours_rag_with_guidance'))

    # methods_experiments.append(find_csv_files('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/main_results/ours_with_guidance_1207_all'))



    window_size = 61

    for experiments in methods_experiments:
        exp_name, csv_file_path = experiments
        result_list, guidance_nums = parse_completion_rates(csv_file_path)
        avg_success_rate, success_rate_dict = calculation(result_list)

        worse_cases, scores = find_tasks_with_declining_success(success_rate_dict)
        for task in worse_cases:
            print(task)
            print("first:",scores[task][0], " second:",scores[task][1], " third:",scores[task][2])
        print(len(worse_cases))





        # # 计算成功率的滑动平均并绘制曲线
        # success_rate_list=[]
        # for data in success_rate_dict:
        #     success_rate_list.append(data['suc_rate'])
        # success_moving_averages = calculate_moving_average(success_rate_list, window_size)
        # plot_output_path = f'main_results/{exp_name}_success_rate_moving_average_plot.png'
        # plot_moving_average(success_moving_averages, plot_output_path, f'Average Success Rate', f'{exp_name} Average Success Rate')

        # # 计算 Guidance query times 的滑动平均并绘制曲线
        # guidance_moving_averages = calculate_moving_average(guidance_nums, window_size)
        # guidance_plot_output_path = f'main_results/{exp_name}_guidance_moving_average_plot.png'
        # plot_moving_average(guidance_moving_averages, guidance_plot_output_path, f'Average Guidance Query Times', f'{exp_name} Average Guidance Query Times')

        # print(f'{exp_name} 的结果图表已保存。')