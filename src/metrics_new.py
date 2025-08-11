# ------------------------------------------------------------

# Currently this metric set syntax error as success. However this only suitable for LLM Method. So remember to change it while evaluating other methods.
# ------------------------------------------------------------





import os
import re
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy import stats

# Extend sys.path if needed
sys.path.append('../VirtualHome-HG/scripts')

# External modules (assumed to be provided)
from logic_parser import parse_logic_from_file_path
from utils_eval import get_difficulty_dict


# ------------------------------------------------------------------------------
# 1. Data Parsing
# ------------------------------------------------------------------------------

def parse_info(log_text):
    """
    Extract specific fields from a log text using regex patterns.

    Args:
        log_text (str): The string containing log information.

    Returns:
        dict: Parsed data including:
              {
                'Time consume': <int>,              # in seconds
                'Exp_helper query times': <int>,
                'Guidance query times': <int>,
                'library scale': <str>              # e.g., "100'"
              }
    """
    parsed_data = {}
    parsed_data['Time consume'] = int(
        re.search(r"Time consume: (\d+) seconds", log_text).group(1)
    )
    parsed_data['Exp_helper query times'] = int(
        re.search(r"Exp_helper query times: (\d+)", log_text).group(1)
    )
    parsed_data['Guidance query times'] = int(
        re.search(r"Guidance query times: (\d+)", log_text).group(1)
    )
    parsed_data['Goal generate times'] = int(re.search(r"goal generate times: ([\d']+)", log_text).group(1)) + int(re.search(r"goal correct times: ([\d']+)", log_text).group(1))
    # parsed_data['Goal generate times'] = int(re.search(r"goal generate times: ([\d']+)", log_text).group(1))

    parsed_data['library scale'] = re.search(
        r"library scale: ([\d']+)", log_text
    ).group(1)
    
    return parsed_data


def parse_completion_rates(csv_file_path):
    """
    Parse completion rates from a given CSV file.

    Args:
        csv_file_path (str): The path of the CSV file to parse.

    Returns:
        tuple: (result_list, guidance_nums)
               - result_list (list): A list of dictionaries with success details.
               - guidance_nums (list): A list of 'Guidance query times' for each row.
    """
    df = pd.read_csv(csv_file_path)
    result_list = []
    guidance_nums = []

    for _, row in df.iterrows():
        info = {'Guidance query times': 0}
        
        # Skip rows that do not contain the data we need
        if row['Info'] == 'Info' or row['Task Category'] == 'Evaluation Finished':
            continue
        
        # If not "Syntax Error", parse the log to get detailed info
        # if row['Content'] != 'Syntax Error':
        info = parse_info(row['Info'])
        guidance_nums.append(info['Guidance query times'])

        completion_rate = row['Success Rate']
        debug_result = row['Content']
        end_report = row['Task Category']
        scene_id_str = row['Task Path']
        match = re.search(r"Scene_id:\s*(\d+)", scene_id_str)
        scene_id = match.group(1) if match else None

        # Case 1: Full success (completion_rate == '1')
        if completion_rate == '1':
            result_dict = {
                'task_path': end_report,
                'keystate_completion_rate': True,
                'action_completion_rate': True,
                'success': True,
                'guidance_num': info['Guidance query times'],
                'goal_generate_times': info['Goal generate times'],
                'Scene_id': scene_id,
            }
            result_list.append(result_dict)
            continue

        # Case 2: Syntax error
        # if debug_result == 'Syntax Error':
        #     result_dict = {
        #         'task_path': end_report,
        #         'keystate_completion_rate': False,
        #         'action_completion_rate': False,
        #         'success': 'syntax error',
        #         'guidance_num': info['Guidance query times'],
        #         'Scene_id': scene_id,
        #     }
        #     result_list.append(result_dict)
        #     continue

        # Case 3: Incomplete success (evaluate keystates and/or actions)
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
            'goal_generate_times': info['Goal generate times'],
            'Scene_id': scene_id,
        }
        result_list.append(result_dict)

    return result_list, guidance_nums


def find_csv_files(root_dir):
    """
    Recursively search for 'epoch.csv' files under the specified directory.

    Args:
        root_dir (str): The root directory to start searching.

    Returns:
        tuple or None:
            If found, returns (experiment_name, csv_file_path). 
            Otherwise, returns None.
    """
    for root, dirs, files in os.walk(root_dir):
        if 'epoch.csv' in files:
            experiment_name = os.path.basename(root)
            csv_file_path = os.path.join(root, 'epoch.csv')
            return (experiment_name, csv_file_path)
    return None


# ------------------------------------------------------------------------------
# 2. Data Analysis
# ------------------------------------------------------------------------------

def calculation(result_list):
    """
    Calculate the average success rate of tasks in result_list,
    and generate a success_rate_list with each task's success rate.

    Args:
        result_list (list): A list of dictionaries containing task details 
                            and completion results.

    Returns:
        tuple: (avg_success_rate, success_rate_list)
               - avg_success_rate (float): The average success rate across tasks.
               - success_rate_list (list): A list of dictionaries like
                 [{"task": <task_path>, "suc_rate": <float>}].
    """
    difficulty_dict = get_difficulty_dict()
    
    success_rate_list = []
    sum_success_rate = 0

    for entry in result_list:
        task_success_rate = 0
        task_path = entry['task_path']
        scene_id = entry['Scene_id']

        # Case 1: Syntax error
        if entry['success'] == 'syntax error':
            task_success_rate = 0

        # Case 2: Completely successful
        elif entry['success']:
            task_success_rate = 1

        # Case 3: Partial success or incomplete
        else:
            solution_combination = parse_logic_from_file_path(task_path)
            # If no keystate is needed
            if solution_combination == 'No keystate is needed':
                task_success_rate = entry['action_completion_rate']
            else:
                max_keystate_completion_rate = 0
                # Explore all possible solutions
                for solution in solution_combination:
                    solution_steps_num = 0
                    current_solution_keystate_completion_rate = 0
                    for keystate in solution:
                        keystate_steps_num = difficulty_dict[f'scene_{scene_id}'][task_path][str(solution)][keystate]
                        solution_steps_num += keystate_steps_num
                        if keystate not in entry['keystate_completion_rate']:
                            steps_left = keystate_steps_num
                        else:
                            steps_left = entry['keystate_completion_rate'][keystate]
                        current_solution_keystate_completion_rate += steps_left

                    # Convert from "steps left" to "steps completed ratio"
                    if solution_steps_num == 0:
                        current_solution_keystate_completion_rate = 1
                    else:
                        current_solution_keystate_completion_rate = (
                            solution_steps_num - current_solution_keystate_completion_rate
                        ) / solution_steps_num

                    max_keystate_completion_rate = max(
                        max_keystate_completion_rate, 
                        current_solution_keystate_completion_rate
                    )

                if entry['action_completion_rate'] == 'No actions required':
                    task_success_rate = max_keystate_completion_rate
                else:
                    # Weighted combination of keystate and action success
                    keystate_weight = 2
                    action_weight = 1
                    task_success_rate = (
                        max_keystate_completion_rate * keystate_weight 
                        + entry['action_completion_rate'] * action_weight
                    ) / (keystate_weight + action_weight)

        success_rate_list.append({"task": task_path, "suc_rate": round(task_success_rate, 3), "Scene_id": scene_id})
        sum_success_rate += task_success_rate

    avg_success_rate = sum_success_rate / len(success_rate_list) if success_rate_list else 0
    return avg_success_rate, success_rate_list


def aggregate_success_rates(success_rate_list):
    """
    For multiple success-rate records of the same task, calculate the average success rate.

    Args:
        success_rate_list (list): 
            [
                {"task": "path/to/task_1", "suc_rate": 0.85},
                {"task": "path/to/task_1", "suc_rate": 0.95},
                {"task": "path/to/task_2", "suc_rate": 0.72},
                ...
            ]

    Returns:
        dict: {task_name: average_success_rate}
              e.g. {"path/to/task_1": 0.90, "path/to/task_2": 0.72}
    """
    task_rates = defaultdict(list)
    for item in success_rate_list:
        task_name = item["task"]
        suc_rate = item["suc_rate"]
        task_rates[task_name].append(suc_rate)
    
    averaged_dict = {}
    for t, rates in task_rates.items():
        averaged_dict[t] = sum(rates) / len(rates)

    return averaged_dict


def find_tasks_with_declining_success(tasks):
    """
    Identify tasks whose success rate declines across multiple evaluations.

    Args:
        tasks (list): A list of dictionaries, each containing "task" and "suc_rate".

    Returns:
        tuple: (declining_tasks, scores)
               - declining_tasks (list): A list of task names that have 
                 a decline in success rate.
               - scores (dict): {task_name: (first, second, third)} 
                 The success rates in chronological order.
    """
    task_groups = defaultdict(list)
    for task in tasks:
        task_groups[task["task"]].append(task["suc_rate"])
    
    declining_tasks = []
    scores = {}
    
    for task_name, rates in task_groups.items():
        # Assuming each task can appear 3 times
        if len(rates) != 3:
            continue
        
        first, second, third = rates[0], rates[1], rates[2]
        # Example condition: if the first score is higher than second and third
        if first > second and first > third:
            declining_tasks.append(task_name)
            scores[task_name] = (first, second, third)
            
    return declining_tasks, scores


def compare_methods_performance(methodA_name, success_rate_dict_a, 
                                methodB_name, success_rate_dict_b):
    """
    Compare the success-rate performance of two methods (A and B).

    Args:
        methodA_name (str): Name of method A (for identification in output).
        success_rate_dict_a (list): Success-rate records for method A, 
                                    possibly containing multiple entries for the same task.
        methodB_name (str): Name of method B (for identification in output).
        success_rate_dict_b (list): Success-rate records for method B, 
                                    possibly containing multiple entries for the same task.

    Returns:
        dict: 
            {
                "A_better": [(task, A_success_rate, B_success_rate), ...],
                "B_better": [(task, A_success_rate, B_success_rate), ...],
                "equal": [(task, A_success_rate, B_success_rate), ...]
            }
    """
    # Aggregate success rates for each method
    task_to_rate_a = aggregate_success_rates(success_rate_dict_a)
    task_to_rate_b = aggregate_success_rates(success_rate_dict_b)

    # Collect all tasks that appeared in either method
    all_tasks = set(task_to_rate_a.keys()) | set(task_to_rate_b.keys())

    A_better = []
    B_better = []
    equal = []

    for task in all_tasks:
        rate_a = task_to_rate_a.get(task, None)
        rate_b = task_to_rate_b.get(task, None)

        # If a task only exists for one method, skip or handle as desired
        if rate_a is None or rate_b is None:
            continue

        if rate_a > rate_b:
            A_better.append((task, rate_a, rate_b))
        elif rate_a < rate_b:
            B_better.append((task, rate_a, rate_b))
        else:
            equal.append((task, rate_a, rate_b))

    result_dict = {
        "A_better": A_better,
        "B_better": B_better,
        "equal": equal
    }

    # Print output (optional)
    print(f"{methodA_name} performs better on:")
    for t, a, b in A_better:
        print(f"  Task: {t}, {methodA_name}: {a:.3f}, {methodB_name}: {b:.3f}")

    print(f"\n{methodB_name} performs better on:")
    for t, a, b in B_better:
        print(f"  Task: {t}, {methodA_name}: {a:.3f}, {methodB_name}: {b:.3f}")

    print(f"\nThey perform the same on:")
    for t, a, b in equal:
        print(f"  Task: {t}, {methodA_name}: {a:.3f}, {methodB_name}: {b:.3f}")

    return result_dict


# ------------------------------------------------------------------------------
# 3. Data Visualization
# ------------------------------------------------------------------------------

def calculate_moving_average(data_list, window_size):
    """
    Calculate the moving average of a list of values using a specified window size.

    Args:
        data_list (list): The list of numeric data.
        window_size (int): The size of the moving average window.

    Returns:
        list: A list containing the moving averages.
    """
    moving_averages = []
    for i in range(len(data_list) - window_size + 1):
        window = data_list[i:i + window_size]
        moving_average = sum(window) / window_size
        moving_averages.append(moving_average)
    return moving_averages


def plot_moving_average(moving_averages, output_path, ylabel, title):
    """
    Plot a curve of the moving average values and save the figure.

    Args:
        moving_averages (list): The moving average values to plot.
        output_path (str): The path to save the output figure.
        ylabel (str): Label for the Y-axis.
        title (str): The title of the plot.
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


def print_success_rates_descending(success_rate_list):
    """
    Sort and print the success rates (from the result list) in descending order,
    with a more visually friendly, column-aligned format.

    Args:
        success_rate_list (list): A list of dictionaries,
            each containing the keys "task" and "suc_rate". For example:
            [
                {"task": "path/to/task_1", "suc_rate": 0.85},
                {"task": "path/to/task_2", "suc_rate": 0.95},
                ...
            ]
    """
    # Sort by "suc_rate" descending
    sorted_rates = sorted(success_rate_list, key=lambda x: x["suc_rate"], reverse=True)

    # Determine the maximum string length of any task name for alignment
    if not sorted_rates:
        print("No success rates to display.")
        return
    max_task_length = max(len(item["task"]) for item in sorted_rates)

    # Print table header
    print(f"{'Rank':<5} {'Task':<{max_task_length}} {'Success Rate':>12}")
    print("-" * (5 + 1 + max_task_length + 1 + 12))

    # Print each task in descending order of success rate
    for i, item in enumerate(sorted_rates, start=1):
        print(f"{i:<5} {item['task']:<{max_task_length}} {item['suc_rate']:>12.3f}")
        with open('success_rates.txt', 'a') as f:
            f.write(f"{i:<5} {item['task']:<{max_task_length}} {item['suc_rate']:>12.3f}\n")

def print_compare_table(data):
    # First, combine methods from different scenes
    combined_data = {}
    method_groups = {
        'CAP': ['CAPWG', 'CAPWG1', 'CAPWG2'],
        'LLM': ['LLMWG', 'LLMWG1', 'LLMWG2'],
        'LLMPlusP': ['LLMPlusPWG', 'LLMPlusPWG1', 'LLMPlusPWG2'],
        'OursWG': ['OursWG'],
        'PvP': ['PvP']
    }

    # Combine data for each method group
    for group_name, method_list in method_groups.items():
        combined_data[group_name] = {}
        all_tasks = set()
        
        # Collect all tasks from all scenes
        for method in method_list:
            if method in data:
                all_tasks.update(data[method].keys())
        
        # Calculate average for each task
        for task in all_tasks:
            task_rates = []
            for method in method_list:
                if method in data and task in data[method]:
                    task_rates.append(data[method][task])
            if task_rates:
                combined_data[group_name][task] = sum(task_rates) / len(task_rates)

    # Create header and rows
    header = ["Task"] + list(combined_data.keys())
    rows = []
    rows.append(header)

    # Get all unique tasks (without scene information)
    all_tasks = set()
    for task in {task for method_dict in combined_data.values() for task in method_dict}:
        base_task = task.split('_scene_')[0] if '_scene_' in task else task
        all_tasks.add(base_task)

    # Add task rows
    for task in sorted(all_tasks):
        row = [task]
        for method in combined_data:
            # For overall methods, calculate average across scenes
            if method in ['OursWG', 'PvP']:
                scene_rates = []
                for scene in range(3):  # 0, 1, 2
                    scene_task = f"{task}_scene_{scene}"
                    if scene_task not in combined_data[method]:
                        raise ValueError(f"Missing data for {scene_task} in {method}")
                    scene_rates.append(combined_data[method][scene_task])
                val = sum(scene_rates) / 3
            else:
                if task not in combined_data[method]:
                    raise ValueError(f"Missing data for {task} in {method}")
                val = combined_data[method][task]
            
            if isinstance(val, float):
                val = f"{val:.3f}"
            row.append(str(val))
        rows.append(row)

    # Prepare column widths for formatting
    num_cols = len(header)
    col_widths = []
    for col_idx in range(num_cols):
        max_w = max(len(r[col_idx]) for r in rows)
        col_widths.append(max_w)

    def format_row(row_data):
        formatted = []
        for i, cell in enumerate(row_data):
            if i == 0:
                formatted.append(cell.ljust(col_widths[i]))
            else:
                formatted.append(cell.rjust(col_widths[i]))
        return " | ".join(formatted)

    # Print the table header
    print(format_row(rows[0]))
    print("-+-".join("-" * w for w in col_widths))

    # Print all task rows
    for row in rows[1:]:
        print(format_row(row))

    # Calculate the average success rate for each method and add it to the last row
    avg_row = ["Avg."]
    for method in combined_data:
        rates = []
        for task in all_tasks:
            if method in ['OursWG', 'PvP']:
                scene_rates = []
                for scene in range(3):
                    scene_task = f"{task}_scene_{scene}"
                    if scene_task not in combined_data[method]:
                        raise ValueError(f"Missing data for {scene_task} in {method}")
                    scene_rates.append(combined_data[method][scene_task])
                rates.append(sum(scene_rates) / 3)
            else:
                if task not in combined_data[method]:
                    raise ValueError(f"Missing data for {task} in {method}")
                rates.append(combined_data[method][task])
        
        avg_rate = sum(rates) / len(rates)
        avg_row.append(f"{avg_rate:.3f}")

    # Print the average success rate row
    print(format_row(avg_row))


# ------------------------------------------------------------------------------
# 4. Main Entry Point
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    """
    Example usage for running the main script. 
    Modify paths or logic as needed for your specific experiments.
    """
    methods_experiments = []

    # Example of finding CSV files:
    # methods_experiments.append(find_csv_files('/path/to/experiment_A'))
    # methods_experiments.append(find_csv_files('/path/to/experiment_B'))
    # ...

    # Scene_0

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250211_162728_LLMWOG'
    # ))


    methods_experiments.append(find_csv_files(
      'main_results/openai_new/round7/scene_0/20250314_141004_LLMWG'
    ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_0/20250209_021552_LLMPlusPWOG'
    ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_0/20250210_005803_LLMPlusPWG'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250209_065056_CAPWOG'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_0/20250210_005839_CAPWG'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250211_104046_WOLibrary'
    # ))


    # Scene_1

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250211_191433_LLMWOG1'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_1/20250211_191421_LLMWG1'
    ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_1/20250213_094201_LLMPlusPWG1'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250210_154842_LLMPlusPWOG1'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250210_084239_CAPWOG1'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_1/20250210_154927_CAPWG1'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250212_025302_WOLibrary1'
    # ))

    # # Scene_2
    
    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_191609_LLMWOG2'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_2/20250211_191553_LLMWG2'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250210_110634_LLMPlusPWOG2'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_2/20250211_021801_LLMPlusPWG2'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_022135_CAPWOG2'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/scene_2/20250211_022106_CAPWG2'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250212_025402_WOLibrary2'
    # ))

    #overall
    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/overall/OursWG'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/overall/OursWOG'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/overall/20250314_151127_PvP'
    ))

    # methods_experiments.append(find_csv_files(
    #     "main_results/openai_new/round7/overall/20250315_151531_PvPWOG"
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/overall/20250212_110306_WORefinement'
    # ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/overall/Action_library'
    ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/overall/ActionLibraryWOG'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/overall/WOSplit'
    # ))

    window_size = 70  # Example window size for moving average

    compare_data = {}
    print_compare_data = {}

    with open('mapping.json', 'r') as file:
        mapping = json.load(file)
    with open('Category_abl.json', 'r') as file:
        category = json.load(file)
    with open('experiments/virtualhome/VH_scripts/shuffled_task_scene_pairs.json', 'r') as file:
        experiment_oder = json.load(file)
    # Process each experiment

    goal_generate_times = []

    OursWOG_moving_average = []
    PVPWOG_moving_average = []
    Ours_action_library_moving_average = []


    for experiment in methods_experiments:
        # Skip if no CSV file was found

        if experiment is None:
            continue

        exp_name, csv_file_path = experiment
        exp_name = exp_name.split('_')[-1]
        result_list, guidance_nums = parse_completion_rates(csv_file_path)

        prefix = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/'

        # filter1
        # ------------------------------
        # result_list_limit = []
        # for result in result_list:
        #     if prefix+result['task_path'] in mapping['middle'].values():
        #         result_list_limit.append(result)
        # result_list = result_list_limit
        # ------------------------------

        

        # filter2
        # ------------------------------
        # result_list_limit = []
        # for result in result_list:
        #     if result['task_path'] in category['complex']: # cooking, cleaning, laundry, arrangement
        #         result_list_limit.append(result)
        # result_list = result_list_limit
        # ------------------------------

        for result in result_list:
            goal_generate_times.append(result['goal_generate_times'])

        # Calculate average success rate and gather all success rates
        avg_success_rate, success_rate_dict = calculation(result_list)

        success_dict_without_inner_list = {}
        for task in success_rate_dict:
            # For overall methods, keep the full task path including scene information
            if exp_name in ['OursWG', 'PvP', 'Action_library']:
                # Keep the full task path with scene information
                task_path = (
                    task['task']
                    .replace('cdl_dataset/dataset/','')
                    .replace('VirtualHome-HG/dataset/','')
                )+'_scene_'+str(task['Scene_id'])
                success_dict_without_inner_list[task_path] = task['suc_rate']
            else:
                # For other methods, keep the original behavior
                success_dict_without_inner_list[(
                    task['task']
                    .replace('cdl_dataset/dataset/','')
                    .replace('VirtualHome-HG/dataset/','')
                )] = task['suc_rate']

        compare_data[exp_name] = success_dict_without_inner_list
        print_compare_data[exp_name] = success_dict_without_inner_list

        print(f"\nExperiment: {exp_name}")
        print(f"Average Success Rate: {avg_success_rate:.3f}")

        with open('success_rates.txt', 'a') as f:
            f.write(f"\nExperiment: {exp_name}")
            f.write(f"Average Success Rate: {avg_success_rate:.3f}")

        print_success_rates_descending(success_rate_dict)

        # Identify tasks with declining success
        worse_cases, scores = find_tasks_with_declining_success(success_rate_dict)
        print("\nTasks with Declining Success (based on specific criteria):")
        for task in worse_cases:
            print(f"  {task} => first: {scores[task][0]}, second: {scores[task][1]}, third: {scores[task][2]}")
        print(f"Number of tasks with declining success: {len(worse_cases)}")

        # Calculate and plot the moving average of the success rate
        success_rate_values = [data['suc_rate'] for data in success_rate_dict]
        success_moving_averages = calculate_moving_average(success_rate_values, window_size)
        if exp_name == 'OursWOG':
            OursWOG_moving_average = success_moving_averages
        if exp_name == 'PvPWOG':
            PVPWOG_moving_average = success_moving_averages
        if exp_name == 'ActionLibraryWOG':
            Ours_action_library_moving_average = success_moving_averages

        plot_output_path = f'main_results/{exp_name}_success_rate_moving_average_plot.png'
        plot_moving_average(
            success_moving_averages, 
            plot_output_path, 
            'Average Success Rate', 
            f'{exp_name} Average Success Rate'
        )

        # Calculate and plot the moving average of the guidance queries
        guidance_moving_averages = calculate_moving_average(guidance_nums, window_size)
        guidance_plot_output_path = f'main_results/{exp_name}_guidance_moving_average_plot.png'
        plot_moving_average(
            guidance_moving_averages, 
            guidance_plot_output_path, 
            'Average Guidance Query Times', 
            f'{exp_name} Average Guidance Query Times'
        )

        print(f"\nPlots for {exp_name} have been saved.")

    print_compare_table(print_compare_data)

    # goal_generate_times.sort()  # 排序
    # n = len(goal_generate_times)
    # remove_count = int(n * 0.3)  # 计算去掉20%的元素数量

    # remaining_nums = goal_generate_times[:-remove_count]
    # total_sum = sum(remaining_nums)
    # print(total_sum)
    print(f"Goal generate times: {sum(goal_generate_times)}")


    diff_oder = []
    Ours_WOLibrary = []
    LLM_plus_PWOG = []
    Cap_WOG = []
    for task in experiment_oder:
        task_path = task[0]
        scene_id = task[1]
        if scene_id == 0:
            diff_oder.append(compare_data['LLMWOG'][task_path])
            # Ours_WOLibrary.append(compare_data['WOLibrary'][task_path])
            LLM_plus_PWOG.append(compare_data['LLMPlusPWOG'][task_path])
            Cap_WOG.append(compare_data['CAPWOG'][task_path])
        if scene_id == 1:
            diff_oder.append(compare_data['LLMWOG1'][task_path])
            # Ours_WOLibrary.append(compare_data['WOLibrary1'][task_path])
            LLM_plus_PWOG.append(compare_data['LLMPlusPWOG1'][task_path])
            Cap_WOG.append(compare_data['CAPWOG1'][task_path])

        if scene_id == 2:
            diff_oder.append(compare_data['LLMWOG2'][task_path])
            # Ours_WOLibrary.append(compare_data['WOLibrary2'][task_path])
            LLM_plus_PWOG.append(compare_data['LLMPlusPWOG2'][task_path])
            Cap_WOG.append(compare_data['CAPWOG2'][task_path])



    plot_output_path = f'main_results/Reference_difficulty.png'


    LLM_moving_sr = calculate_moving_average(diff_oder, window_size)
    Ours_WOLibrary_moving_sr = calculate_moving_average(Ours_WOLibrary, window_size)
    LLM_plus_PWOG_moving_sr = calculate_moving_average(LLM_plus_PWOG, window_size)
    Cap_WOG_moving_sr = calculate_moving_average(Cap_WOG, window_size)
    
    
    # colors = ['#ff6f61', '#6b8e23', '#4682b4', '#d4a017']
    # x = range(len(LLM_moving_sr))
    # plt.plot(x, LLM_moving_sr, linewidth=3, label="LLM", color=colors[0])
    # plt.plot(x, LLM_plus_PWOG_moving_sr, linewidth=3, label="LLM+P", color=colors[1])
    # plt.plot(x, Cap_WOG_moving_sr, linewidth=3, label="CAP", color=colors[2])
    # plt.plot(x, OursWOG_moving_average, linewidth=3, label="Ours", color=colors[3])
    # plt.grid(axis='y', color='gray', linestyle='--', linewidth=0.5)
    # plt.tick_params(axis='x', labelsize=14)
    # plt.tick_params(axis='y', labelsize=14)

    # plt.xlabel("Tasks", fontsize=18)
    # plt.ylabel("Success Rate", fontsize=18)
    # plt.title("Moving Average Success Rate (window = 70)", fontsize=18)
    # plt.legend(fontsize=18)

    # plt.show()
    # PVPWOG_moving_average add 0 to len(OursWOG_moving_average)

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Define a more vibrant and professional color palette
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#f1c40f']  # Blue, Orange, Green, Red, Yellow
    
    # Create figure with better aspect ratio
    plt.figure(figsize=(15, 8))
    
    # Plot lines with improved styling
    line_styles = ['-', '--', '-.', '-', '-']  # Last line solid
    markers = ['o', 's', '^', 'D', 'o']  # Last marker circle
    marker_sizes = [5, 5, 5, 5, 7]  # Increased last marker size
    line_widths = [2.0, 2.0, 2.0, 2.0, 3.0]  # Increased last line width
    
    x = range(len(LLM_moving_sr))
    
    # Function to plot data and regression line
    def plot_with_regression(x, y, color, label, line_style, marker, marker_size, line_width, markevery):
        # Plot original data
        plt.plot(x, y, linewidth=line_width, label=label, 
                 color=color, linestyle=line_style, 
                 marker=marker, markersize=marker_size, 
                 markevery=markevery)
        
        # Calculate and plot regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        regression_line = slope * np.array(x) + intercept
        plt.plot(x, regression_line, color=color, linestyle='--', linewidth=line_width*0.6, alpha=0.5)
        
        # Add slope value at the right end of the regression line
        end_x = x[-1]
        end_y = slope * end_x + intercept
        
        # Convert slope to custom format (multiply by 1e4 to get rid of e-04)
        slope_formatted = slope * 1e4
        plt.text(end_x + 1, end_y, f'k = {slope_formatted:.1f}', 
                color=color, fontsize=16, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                horizontalalignment='left', verticalalignment='center')
        
        return label
    
    # Plot each line with regression
    labels = []
    labels.append(plot_with_regression(x, LLM_moving_sr, colors[0], "LLM", 
                                     line_styles[0], markers[0], marker_sizes[0], 
                                     line_widths[0], 5))
    labels.append(plot_with_regression(x, LLM_plus_PWOG_moving_sr, colors[1], "LLM+P", 
                                     line_styles[1], markers[1], marker_sizes[1], 
                                     line_widths[1], 5))
    labels.append(plot_with_regression(x, Cap_WOG_moving_sr, colors[2], "CAP", 
                                     line_styles[2], markers[2], marker_sizes[2], 
                                     line_widths[2], 5))
    labels.append(plot_with_regression(x, PVPWOG_moving_average, colors[3], "Voyager", 
                                     line_styles[3], markers[3], marker_sizes[3], 
                                     line_widths[3], 5))
    labels.append(plot_with_regression(x, OursWOG_moving_average, colors[4], "Ours (Full)", 
                                     line_styles[4], markers[4], marker_sizes[4], 
                                     line_widths[4], 5))

    # Customize grid
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Customize axes
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_linewidth(0.5)
    plt.gca().spines['bottom'].set_linewidth(0.5)
    
    # Customize ticks
    plt.tick_params(axis='x', labelsize=16, pad=5)
    plt.tick_params(axis='y', labelsize=16, pad=5)
    
    # Set axis labels with better formatting and position
    plt.xlabel("Number of Tasks", fontsize=18, fontweight='bold', labelpad=10)
    plt.ylabel("Success Rate (%)", fontsize=18, fontweight='bold', labelpad=0)
    
    # Set title with better formatting and position
    plt.title(f"Moving Average Success Rate (window = {window_size})", 
              fontsize=20, fontweight='bold', pad=0, y=1.0)
    
    # Customize legend with correct order
    legend_labels = ["LLM", "LLM+P", "CAP", "Voyager", "Ours (Full)"]
    legend = plt.legend(legend_labels, fontsize=16, loc='lower left', 
                       bbox_to_anchor=(0.02, 0.02),
                       frameon=True, fancybox=True, shadow=True,
                       ncol=2)
    legend.get_frame().set_alpha(0.9)
    
    # Add minor grid lines
    plt.grid(True, which='minor', linestyle=':', alpha=0.2)
    plt.minorticks_on()
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show plot
    plt.show()



# "cdl_dataset/dataset/Cook_some_food/g5.txt"
# "cdl_dataset/dataset/Prepare_breakfast/g4.txt"
# "cdl_dataset/dataset/Cook_some_food/g9.txt"
# "cdl_dataset/dataset/Iron_clothes/g5.txt"
#"cdl_dataset/dataset/Iron_clothes/g6.txt"
# cdl_dataset/dataset/Make_coffee/g1.txt"