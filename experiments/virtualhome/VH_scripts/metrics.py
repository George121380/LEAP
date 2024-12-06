import pandas as pd
import re
import sys
import json
import os
import matplotlib.pyplot as plt

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
    methods_experiments = []
    for root, dirs, files in os.walk(root_dir):
        if 'epoch.csv' in files:
            experiment_name = os.path.basename(root)
            csv_file_path = os.path.join(root, 'epoch.csv')
            methods_experiments.append((experiment_name, csv_file_path))
    return methods_experiments


def parse_completion_rates(csv_file_path):
    df = pd.read_csv(csv_file_path)
    result_list = []
    guidance_nums = []  # 新增：记录 Guidance query times

    for index, row in df.iterrows():
        info = {'Guidance query times': 0}
        if row['Content'] != 'Syntax Error':
            info = parse_info(row['Info'])
        guidance_nums.append(info['Guidance query times'])  # 新增：存储 Guidance query times

        completion_rate = row['Success Rate']
        debug_result = row['Content']
        end_report = row['Task Category']
        task_path = row['Task Path']

        if completion_rate == '1':
            result_dict = {
                'task_path': task_path,
                'keystate_completion_rate': True,
                'action_completion_rate': True,
                'success': True,
                'guidance_num': info['Guidance query times'],
            }
            result_list.append(result_dict)
            continue

        if debug_result == 'Syntax Error':
            result_dict = {
                'task_path': task_path,
                'keystate_completion_rate': False,
                'action_completion_rate': False,
                'success': 'syntax error',
                'guidance_num': info['Guidance query times'],
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
            'task_path': task_path,
            'keystate_completion_rate': keystate_dict,
            'action_completion_rate': action_completion_rate,
            'success': False,
            'guidance_num': info['Guidance query times'],
        }

        result_list.append(result_dict)

    return result_list, guidance_nums


def calculation(result_list):
    difficulty_dict = json.load(open('result.json'))
    success_rate_list = []
    sum_success_rate = 0
    for entry in result_list:
        task_success_rate = 0
        task_path = entry['task_path']
        if task_path not in difficulty_dict:
            continue

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
                        keystate_steps_num = difficulty_dict[task_path][str(solution)][keystate]
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

        success_rate_list.append(round(task_success_rate, 3))
        sum_success_rate += task_success_rate

    avg_success_rate = sum_success_rate / len(success_rate_list)
    return avg_success_rate, success_rate_list


if __name__ == '__main__':
    methods_experiments = find_csv_files('log/main_with_guidance')
    # methods_experiments = find_csv_files('log/main_without_guidance')

    window_size = 50

    for experiments in methods_experiments:
        print(f'正在处理 {experiments} 方法的实验结果...')
        exp_name, csv_file_path = experiments
        result_list, guidance_nums = parse_completion_rates(csv_file_path)
        avg_success_rate, success_rate_dict = calculation(result_list)

        # 计算成功率的滑动平均并绘制曲线
        success_moving_averages = calculate_moving_average(success_rate_dict, window_size)
        plot_output_path = f'baseline_result/{exp_name}_success_rate_moving_average_plot.png'
        plot_moving_average(success_moving_averages, plot_output_path, 'Moving Average Success Rate', 'Moving Average of Success Rate')

        # 计算 Guidance query times 的滑动平均并绘制曲线
        guidance_moving_averages = calculate_moving_average(guidance_nums, window_size)
        guidance_plot_output_path = f'baseline_result/{exp_name}_guidance_moving_average_plot.png'
        plot_moving_average(guidance_moving_averages, guidance_plot_output_path, 'Moving Average Guidance Query Times', 'Moving Average of Guidance Query Times')

        print(f'{exp_name} 的结果图表已保存。')