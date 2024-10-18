import pandas as pd
import re
import sys
sys.path.append('cdl_dataset/scripts')
from logic_parser import parse_logic_from_file_path
import json
import os


def find_csv_files(root_dir):
    """
    从指定根目录中递归查找所有的`epoch.csv`文件并将其按方法和实验名称组织起来。
    
    Args:
    - root_dir (str): 要搜索的根目录路径。
    
    Returns:
    - dict: 一个嵌套字典，键是方法名，值是(实验名, csv文件路径)的列表。
    """
    methods_experiments = {}

    # 遍历根目录及其子目录
    for root, dirs, files in os.walk(root_dir):
        if 'epoch.csv' in files:
            # 提取方法和实验名称
            method_name = os.path.basename(os.path.dirname(root))
            experiment_name = os.path.basename(root)
            csv_file_path = os.path.join(root, 'epoch.csv')

            # 将结果添加到字典中
            if method_name not in methods_experiments:
                methods_experiments[method_name] = []
            methods_experiments[method_name].append((experiment_name, csv_file_path))

    return methods_experiments

def parse_completion_rates(csv_file_path):
    df = pd.read_csv(csv_file_path)
    result_list = []

    for index, row in df.iterrows():
        completion_rate = row['LLM Answer']
        debug_result = row['Debug Result']
        end_report = row['Goal Representation']

        task_path = row['Plan']

        if completion_rate == '1':
            result_dict = {
                'task_path': task_path,
                'keystate_completion_rate': True,
                'action_completion_rate': True,
                'success': True
            }
            result_list.append(result_dict)
            continue

        if debug_result == 'Syntax Error':
            result_dict = {
                'task_path': task_path,
                'keystate_completion_rate': False,
                'action_completion_rate': False,
                'success': 'syntax error'
            }
            result_list.append(result_dict)
            continue

        if end_report == 'Evaluation Finished':
            continue

        keystate_matches = re.findall(r'(Keystate: k\d+) - Completion Rate: ([\d.]+)', completion_rate)
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
            'success': False
        }

        result_list.append(result_dict)

    return result_list

def calculation(result_list):
    difficulty_dict = json.load(open('cdl_dataset/difficulty_counting.json'))
    success_rate_dict = {}
    sum_success_rate = 0
    for entry in result_list:
        task_success_rate = 0
        task_path = entry['task_path']
        if task_path == 'cdl_dataset/dataset/Put_groceries_in_Fridge/g4.txt':
            print('debug')
        if entry['success'] == 'syntax error':
            task_success_rate = 0
        elif entry['success']:
            task_success_rate = 1
        else:
            if entry['keystate_completion_rate'] == {}:
                task_success_rate = 0
                print('No keystate is recorded')
            else:
                solution_combination = parse_logic_from_file_path(task_path)
                if solution_combination == 'No keystate is needed':
                    task_success_rate = entry['action_completion_rate']
                else:
                    max_keystate_completion_rate = 0
                    dict_flag = True

                    for solution in solution_combination:
                        for keystate in solution:
                            assert keystate in entry['keystate_completion_rate']
                            if task_path not in difficulty_dict:
                                dict_flag = False
                                print(f'{task_path} not in difficulty_dict')
                                break
                            if keystate not in difficulty_dict[task_path]:
                                dict_flag = False
                                print(f'{keystate} not in difficulty_dict')
                                break

                    for solution in solution_combination:
                        solution_steps_num = 0
                        current_solution_keystate_completion_rate = 0

                        for keystate in solution:
                            if dict_flag:
                                keystate_steps_num = difficulty_dict[task_path][keystate]
                                solution_steps_num += keystate_steps_num
                                current_solution_keystate_completion_rate += entry['keystate_completion_rate'][keystate] * keystate_steps_num
                            else:
                                current_solution_keystate_completion_rate += entry['keystate_completion_rate'][keystate]
                                solution_steps_num += 1

                        current_solution_keystate_completion_rate /= solution_steps_num
                        max_keystate_completion_rate = max(max_keystate_completion_rate, current_solution_keystate_completion_rate)

                    if entry['action_completion_rate'] == 'No actions required':
                        task_success_rate = max_keystate_completion_rate
                    else:
                        keystate_weight = 2
                        action_weight = 1
                        task_success_rate = (max_keystate_completion_rate * keystate_weight + entry['action_completion_rate'] * action_weight) / (keystate_weight + action_weight)

        success_rate_dict[task_path] = round(task_success_rate,3)
        sum_success_rate += task_success_rate

    avg_success_rate = sum_success_rate / len(success_rate_dict)
    return avg_success_rate, success_rate_dict

def aggregate_success_rates_per_task(methods_experiments_results):
    """
    汇总不同方法和实验的任务成功率。

    Args:
    - methods_experiments_results (dict): 一个嵌套字典，键是方法名，值是(实验名, success_rate_dict)的列表。

    Returns:
    - pd.DataFrame: 行是任务，列是方法的各次实验成功率，以及每个方法的平均成功率。
    """
    all_tasks = set()
    for method_results in methods_experiments_results.values():
        for _, success_rate_dict in method_results:
            all_tasks.update(success_rate_dict.keys())

    all_tasks = sorted(all_tasks)
    df = pd.DataFrame(index=all_tasks)

    for method_name, experiments in methods_experiments_results.items():
        experiment_names = []
        for exp_name, success_rate_dict in experiments:
            experiment_names.append(exp_name)
            column_name = f'{method_name}_{exp_name}'
            df[column_name] = df.index.map(success_rate_dict)

        # 计算每个方法的平均成功率
        method_columns = [f'{method_name}_{exp_name}' for exp_name in experiment_names]
        df[f'{method_name}_average'] = round(df[method_columns].mean(axis=1),3)

    return df

def best_method_per_task(df):
    """
    生成只包含每个方法的平均值的表格，并找到每个任务上表现最好的方法。

    Args:
    - df (pd.DataFrame): 包含每个方法各次实验的成功率和平均值的DataFrame。

    Returns:
    - pd.DataFrame: 只包含每个任务上各方法的平均成功率，以及每个任务上表现最好的方法的表格。
    """
    method_columns = [col for col in df.columns if 'average' in col]
    avg_df = df[method_columns].copy()

    # 找到每个任务平均值最高的方法
    avg_df['best_method'] = avg_df.idxmax(axis=1)

    return avg_df

def best_method_sorted_by_max_avg(df):
    """
    生成只包含每个任务各方法的平均成功率表格，并按任务的最高平均成功率从小到大排序。

    Args:
    - df (pd.DataFrame): 包含每个方法各次实验的成功率和平均值的DataFrame。

    Returns:
    - pd.DataFrame: 只包含每个任务上各方法的平均成功率，按照每个任务的最高平均成功率从小到大排序。
    """
    # 筛选包含 'average' 的列，也就是各方法的平均成功率
    method_columns = [col for col in df.columns if 'average' in col]
    avg_df = df[method_columns].copy()

    # 找到每个任务的最高平均成功率
    avg_df['max_avg_success'] = avg_df.max(axis=1)

    # 按最高平均成功率从小到大排序
    avg_df_sorted = avg_df.sort_values(by='max_avg_success', ascending=True)

    return avg_df_sorted


def save_to_csv(dataframe, output_path):
    """
    将汇总的成功率保存到CSV文件。

    Args:
    - dataframe (pd.DataFrame): 要保存的DataFrame。
    - output_path (str): CSV文件的保存路径。
    """
    dataframe.to_csv(output_path, index=True)

if __name__ == '__main__':
    methods_experiments = find_csv_files('baseline_result')

    methods_experiments_results = {}

    for method_name, experiments in methods_experiments.items():
        method_results = []
        for exp_name, csv_file_path in experiments:
            result_list = parse_completion_rates(csv_file_path)
            avg_success_rate, success_rate_dict = calculation(result_list)
            method_results.append((exp_name, success_rate_dict))
        methods_experiments_results[method_name] = method_results

    # 汇总表格1：包含所有实验结果
    aggregated_df = aggregate_success_rates_per_task(methods_experiments_results)
    save_to_csv(aggregated_df, 'baseline_result/aggregated_success_rates.csv')
    print('汇总的成功率已保存到 aggregated_success_rates.csv')

    # 表格2：只包含方法的平均成功率和最佳方法
    avg_df = best_method_per_task(aggregated_df)
    save_to_csv(avg_df, 'baseline_result/best_method_per_task.csv')
    print('平均成功率和最佳方法已保存到 best_method_per_task.csv')

    # 表格3：按照平均成功率排序的方法
    sorted_avg_df = best_method_sorted_by_max_avg(aggregated_df)
    save_to_csv(sorted_avg_df, 'baseline_result/sorted_methods_by_avg_success_rate.csv')
    print('方法按照平均成功率排序的表格已保存到 sorted_methods_by_avg_success_rate.csv')

    # 可选：打印每个方法的平均成功率
    for method_name in methods_experiments.keys():
        avg_success_rate = aggregated_df[f'{method_name}_average'].mean()
        print(f'{method_name} 的平均成功率: {avg_success_rate}')
