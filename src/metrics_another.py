"""
Alternative Metrics Analysis Implementation

This module provides an alternative implementation of metrics analysis:
- Different statistical approaches and calculation methods
- Alternative visualization and comparison techniques
- Experimental metrics and evaluation approaches
- Backup analysis tools and validation methods
- Research-oriented analysis functions

Alternative metrics implementation for comparative analysis and validation.
"""





import os
import re
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Extend sys.path if needed
sys.path.append('../VirtualHome-HG/scripts')
from action_sequence_parser import parse_action_sequence_from_file_path

# External modules (assumed to be provided)
from logic_parser import parse_logic_from_file_path
from utils.utils import get_difficulty_dict


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
        action_sequences = parse_action_sequence_from_file_path(task_path,scene_id)
        if action_sequences == []:
            required_action_len = 0
        else:
            required_action_len = len(action_sequences[0])

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
                # Explore all possible solutions
                for solution in solution_combination:
                    solution_required_steps_num = 0
                    current_solution_steps_left = 0
                    for keystate in solution:
                        keystate_required_steps_num = difficulty_dict[f'scene_{scene_id}'][task_path][str(solution)][keystate]
                        solution_required_steps_num += keystate_required_steps_num
                        if keystate not in entry['keystate_completion_rate']:
                            steps_left = keystate_required_steps_num
                        else:
                            steps_left = entry['keystate_completion_rate'][keystate]
                        current_solution_steps_left += steps_left

                    current_solution_steps_left = min(solution_required_steps_num, current_solution_steps_left)

                    if entry['action_completion_rate'] != 'No actions required':
                
                        task_success_rate = (solution_required_steps_num - current_solution_steps_left + (entry['action_completion_rate'] * required_action_len) * 2) / (solution_required_steps_num + required_action_len * 2)
                    
                    else:
                        task_success_rate = (solution_required_steps_num - current_solution_steps_left) / solution_required_steps_num

        success_rate_list.append({"task": task_path, "suc_rate": round(task_success_rate, 3)})
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

def print_compare_table(data):
    methods = sorted(data.keys())
    tasks = sorted({task for method_dict in data.values() for task in method_dict})

    header = ["Task"] + methods

    rows = []
    rows.append(header)

    # Add all task success rates to the table
    for task in tasks:
        row = [task]
        for m in methods:
            val = data[m].get(task, "")
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
    for m in methods:
        rates = data[m].values()
        if rates:  # Handle empty case to prevent errors
            avg_rate = sum(rates) / len(rates)
        else:
            avg_rate = 0.0
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

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250211_104009_LLMWG'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250209_021552_LLMPlusPWOG'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250210_005803_LLMPlusPWG'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250209_065056_CAPWOG'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250210_005839_CAPWG'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_0/20250211_104046_WOLibrary'
    # ))


    # Scene_1

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250211_191433_LLMWOG1'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250211_191421_LLMWG1'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250210_154842_LLMPlusPWOG1'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250210_084239_CAPWOG1'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250210_154927_CAPWG1'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_1/20250212_025302_WOLibrary1'
    # ))

    # # Scene_2
    
    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_191609_LLMWOG2'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_191553_LLMWG2'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250210_110634_LLMPlusPWOG2'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_021801_LLMPlusPWG2'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_022135_CAPWOG2'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250211_022106_CAPWG2'
    # ))

    # methods_experiments.append(find_csv_files(
    #     'main_results/openai_new/round7/scene_2/20250212_025402_WOLibrary2'
    # ))

    #overall
    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/overall/OursWG'
    ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/overall/OursWOG'
    ))

    methods_experiments.append(find_csv_files(
        'main_results/openai_new/round7/overall/20250212_110306_WORefinement'
    ))

    window_size = 1  # Example window size for moving average

    compare_data = {}

    with open('mapping.json', 'r') as file:
        mapping = json.load(file)
    with open('Category.json', 'r') as file:
        category = json.load(file)
    # Process each experiment

    goal_generate_times = []

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
        #     if result['task_path'] in category['arrangement']: # cooking, cleaning, laundry, arrangement
        #         result_list_limit.append(result)
        # result_list = result_list_limit
        # ------------------------------

        for result in result_list:
            goal_generate_times.append(result['goal_generate_times'])

        # Calculate average success rate and gather all success rates
        avg_success_rate, success_rate_dict = calculation(result_list)

        success_dict_without_inner_list = {}
        for task in success_rate_dict:

            success_dict_without_inner_list[task['task'].replace('cdl_dataset/dataset/','')] = task['suc_rate']

        compare_data[exp_name] = success_dict_without_inner_list

        print(f"\nExperiment: {exp_name}")
        print(f"Average Success Rate: {avg_success_rate:.3f}")

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

    print_compare_table(compare_data)

    # goal_generate_times.sort()  # Sort the data
    # n = len(goal_generate_times)
    # remove_count = int(n * 0.3)  # Calculate number of elements to remove (30%)

    # remaining_nums = goal_generate_times[:-remove_count]
    # total_sum = sum(remaining_nums)
    # print(total_sum)
    print(f"Goal generate times: {sum(goal_generate_times)}")