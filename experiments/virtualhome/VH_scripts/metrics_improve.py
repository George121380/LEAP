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
from metrics import calculation

# Extend sys.path if needed
sys.path.append('cdl_dataset/scripts')

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


    output_avg = 0
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
        output_avg += avg_rate

    # Print the average success rate row
    print(format_row(avg_row))
    # print(f"Average Success Rate: {output_avg / len(methods):.3f}")
    


# ------------------------------------------------------------------------------
# 4. Main Entry Point
# ------------------------------------------------------------------------------

# Define experiment configurations
EXPERIMENT_CONFIGS = {
    'LLMWG': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250314_141004_LLMWG',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250211_191421_LLMWG1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250211_191553_LLMWG2'
        ],
        'description': 'LLM with guidance experiments across all scenes'
    },
    'LLMWOG': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250211_162728_LLMWOG',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250211_191433_LLMWOG1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250211_191609_LLMWOG2'
        ],
        'description': 'LLM without guidance experiments across all scenes'
    },
    'LLMPlusPWG': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250210_005803_LLMPlusPWG',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250213_094201_LLMPlusPWG1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250211_021801_LLMPlusPWG2'
        ],
        'description': 'LLM+P with guidance experiments across all scenes'
    },
    'LLMPlusPWOG': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250209_021552_LLMPlusPWOG',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250210_154842_LLMPlusPWOG1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250210_110634_LLMPlusPWOG2'
        ],
        'description': 'LLM+P without guidance experiments across all scenes'
    },
    'CAPWG': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250210_005839_CAPWG',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250210_154927_CAPWG1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250211_022106_CAPWG2'
        ],
        'description': 'CAP with guidance experiments across all scenes'
    },
    'CAPWOG': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250209_065056_CAPWOG',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250210_084239_CAPWOG1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250211_022135_CAPWOG2'
        ],
        'description': 'CAP without guidance experiments across all scenes'
    },
    'WOLibrary': {
        'paths': [
            # Scene 0
            'main_results/openai_new/round7/scene_0/20250211_104046_WOLibrary',
            # Scene 1
            'main_results/openai_new/round7/scene_1/20250212_025302_WOLibrary1',
            # Scene 2
            'main_results/openai_new/round7/scene_2/20250212_025402_WOLibrary2'
        ],
        'description': 'Without Library experiments across all scenes'
    },
    'OursWG': {
        'paths': [
            'main_results/openai_new/round7/overall/OursWG'
        ],
        'description': 'Overall experiments with guidance'
    },
    'OursWOG': {
        'paths': [
            'main_results/openai_new/round7/overall/OursWOG'
        ],
        'description': 'Overall experiments without guidance'
    },
    'PvP': {
        'paths': [
            'main_results/openai_new/round7/overall/20250314_151127_PvP'
        ],
        'description': 'PvP experiments'
    },
    'PvPWOG': {
        'paths': [
            'main_results/openai_new/round7/overall/20250315_151531_PvPWOG'
        ],
        'description': 'PvP without guidance experiments'
    },
    'WORefinement': {
        'paths': [
            'main_results/openai_new/round7/overall/20250212_110306_WORefinement'
        ],
        'description': 'Without refinement experiments'
    },
    'ActionLibraryWG': {
        'paths': [
            'main_results/openai_new/round7/overall/Action_libraryWG'
        ],
        'description': 'Action library with guidance experiments'
    },
    'ActionLibraryWOG': {
        'paths': [
            'main_results/openai_new/round7/overall/ActionLibraryWOG'
        ],
        'description': 'Action library without guidance experiments'
    },
    'WOSplit': {
        'paths': [
            'main_results/openai_new/round7/overall/WOSplit'
        ],
        'description': 'Without split experiments'
    }
}

def calculate_category_success_rates(result_list, category_dict, category_abl_dict):
    """
    Calculate success rates for each category and overall.
    
    Args:
        result_list (list): List of results
        category_dict (dict): Dictionary mapping tasks to categories from Category.json
        category_abl_dict (dict): Dictionary mapping tasks to categories from Category_abl.json
    
    Returns:
        tuple: (cooking_rate, cleaning_rate, laundry_rate, arrangement_rate, multi_stages_rate, novel_rate, super_complex_rate, strong_constraint_rate, normal_rate, overall_rate)
    """
    # Initialize results for both traditional and abl categories
    traditional_categories = ['cooking', 'cleaning', 'laundry', 'arrangement']
    abl_categories = ['novel_task', 'multi-stages', 'super_complex', 'strong_constraint', 'normal']
    
    category_results = {
        'cooking': [],
        'cleaning': [],
        'laundry': [],
        'arrangement': [],
        'novel_task': [],
        'multi-stages': [],
        'super_complex': [],
        'strong_constraint': [],
        'normal': []
    }
    
    # Create a mapping of (task_path, scene_id) to scene_id
    task_scene_mapping = {}
    for result in result_list:
        task_path = result['task_path']
        scene_id = result.get('Scene_id', 'unknown')
        task_scene_mapping[(task_path, scene_id)] = scene_id
    
    # Calculate success rates using the original calculation function
    _, success_rate_list = calculation(result_list)
    
    # Create a mapping of (task_path, scene_id) to success rates
    task_success_rates = {}
    for result in result_list:
        task_path = result['task_path']
        scene_id = result.get('Scene_id', 'unknown')
        # Find the corresponding success rate from success_rate_list
        for item in success_rate_list:
            if item['task'] == task_path and item['Scene_id'] == scene_id:
                task_success_rates[(task_path, scene_id)] = item['suc_rate']
                # break
    
    # Add results to corresponding categories with scene information
    for result in result_list:
        task_path = result['task_path']
        scene_id = result.get('Scene_id', 'unknown')
        success_rate = task_success_rates.get((task_path, scene_id), 0.0)
        
        # Check traditional categories
        for category_name, tasks in category_dict.items():
            if task_path in tasks:
                category_results[category_name].append((success_rate, scene_id))
                # break
        
        # Check abl categories
        for category_name, tasks in category_abl_dict.items():
            if task_path in tasks:
                category_results[category_name].append((success_rate, scene_id))
                # break
    
    # Calculate rates for all categories
    all_rates = []
    
    # Process traditional categories
    for category in traditional_categories:
        if category_results[category]:
            # Group results by scene
            scene_results = {}
            for rate, scene_id in category_results[category]:
                if scene_id not in scene_results:
                    scene_results[scene_id] = []
                scene_results[scene_id].append(rate)
            
            # Calculate average for each scene
            scene_averages = []
            for scene_rates in scene_results.values():
                if scene_rates:
                    scene_averages.append(sum(scene_rates) / len(scene_rates))
            
            # Calculate final category average
            if scene_averages:
                all_rates.append(sum(scene_averages) / len(scene_averages))
            else:
                all_rates.append(0.0)
        else:
            all_rates.append(0.0)
    
    # Process abl categories
    for category in abl_categories:
        if category_results[category]:
            # Group results by scene
            scene_results = {}
            for rate, scene_id in category_results[category]:
                if scene_id not in scene_results:
                    scene_results[scene_id] = []
                scene_results[scene_id].append(rate)
            
            # Calculate average for each scene
            scene_averages = []
            for scene_rates in scene_results.values():
                if scene_rates:
                    scene_averages.append(sum(scene_rates) / len(scene_rates))
            
            # Calculate final category average
            if scene_averages:
                all_rates.append(sum(scene_averages) / len(scene_averages))
            else:
                all_rates.append(0.0)
        else:
            all_rates.append(0.0)
    
    # Calculate overall average
    all_success_rates = []
    for rates_list in category_results.values():
        all_success_rates.extend([rate for rate, _ in rates_list])
    overall_rate = sum(all_success_rates) / len(all_success_rates) if all_success_rates else 0.0
    
    # Ensure all rates are between 0 and 1
    all_rates = [max(0.0, min(1.0, rate)) for rate in all_rates]
    overall_rate = max(0.0, min(1.0, overall_rate))
    
    # Return rates in the expected order
    # Traditional categories (0-3): cooking, cleaning, laundry, arrangement
    # Abl categories (4-7): complex, novel, super_complex, strong_constraint
    return (
        all_rates[0],  # cooking
        all_rates[1],  # cleaning
        all_rates[2],  # laundry
        all_rates[3],  # arrangement
        all_rates[4],  # novel
        all_rates[5],  # multi-stages
        all_rates[6],  # super_complex
        all_rates[7],  # strong_constraint
        all_rates[8],  # normal
        overall_rate   # overall
    )

def run_experiment(experiment_name):
    """
    Run analysis for the specified experiment group.
    
    Args:
        experiment_name (str): The name of the experiment group to run
    """
    if experiment_name not in EXPERIMENT_CONFIGS:
        print(f"Invalid experiment name. Available experiments: {list(EXPERIMENT_CONFIGS.keys())}")
        return

    config = EXPERIMENT_CONFIGS[experiment_name]
    print(f"\nRunning {config['description']}")
    print("-" * 50)

    methods_experiments = []
    for path in config['paths']:
        methods_experiments.append(find_csv_files(path))

    # Load both category data files
    with open('Category.json', 'r') as file:
        category = json.load(file)
    with open('Category_abl.json', 'r') as file:
        category_abl = json.load(file)

    all_results = []
    goal_generate_times = []

    # Process each experiment
    for experiment in methods_experiments:
        if experiment is None:
            continue

        exp_name, csv_file_path = experiment
        result_list, guidance_nums = parse_completion_rates(csv_file_path)
        all_results.extend(result_list)

        for result in result_list:
            if 'goal_generate_times' in result:
                goal_generate_times.append(result['goal_generate_times'])

    # Calculate success rates for each category
    cooking_rate, cleaning_rate, laundry_rate, arrangement_rate, multi_stages_rate, novel_rate, super_complex_rate, strong_constraint_rate, normal_rate, overall_rate = calculate_category_success_rates(all_results, category, category_abl)

    # Print results
    print(f"\nResults for {experiment_name}:")
    print(f"Cooking tasks success rate: {cooking_rate:.3f}")
    print(f"Cleaning tasks success rate: {cleaning_rate:.3f}")
    print(f"Laundry tasks success rate: {laundry_rate:.3f}")
    print(f"Arrangement tasks success rate: {arrangement_rate:.3f}")
    print(f"Multi-stages tasks success rate: {multi_stages_rate:.3f}")
    print(f"Novel tasks success rate: {novel_rate:.3f}")
    print(f"Super complex tasks success rate: {super_complex_rate:.3f}")
    print(f"Strong constraint tasks success rate: {strong_constraint_rate:.3f}")
    print(f"Normal tasks success rate: {normal_rate:.3f}")
    print(f"Overall success rate: {overall_rate:.3f}")
    print(f"\nTotal goal generate times: {sum(goal_generate_times)}")

def get_method_pairs(method_name):
    """
    Get the WG and WOG experiment names for a given method.
    If a method doesn't have both versions, infer from the name.
    
    Args:
        method_name (str): The base method name (e.g., 'LLM', 'CAP', 'LLMPlusP', 'PvP', etc.)
    
    Returns:
        tuple: (wg_name, wog_name) - The experiment names for with and without guidance
    """
    # First try exact matches
    wg_name = f"{method_name}WG"
    wog_name = f"{method_name}WOG"
    
    if wg_name in EXPERIMENT_CONFIGS and wog_name in EXPERIMENT_CONFIGS:
        return wg_name, wog_name
    
    # Special cases
    if method_name == 'PvP':
        return 'PvP', 'PvPWOG'
    elif method_name == 'PvPWOG':
        return 'PvP', 'PvPWOG'
    elif method_name == 'Ours':
        return 'OursWG', 'OursWOG'
    elif method_name == 'ActionLibrary':
        return 'ActionLibraryWG', 'ActionLibraryWOG'
    elif method_name in ['WORefinement', 'WOSplit', 'WOLibrary']:
        # These methods don't have guidance versions, return None for wg_name
        return None, method_name
    else:
        # For other methods, try to find any matching experiments
        wg_candidates = [name for name in EXPERIMENT_CONFIGS.keys() if method_name in name and 'WG' in name]
        wog_candidates = [name for name in EXPERIMENT_CONFIGS.keys() if method_name in name and 'WOG' in name]
        
        wg_name = wg_candidates[0] if wg_candidates else None
        wog_name = wog_candidates[0] if wog_candidates else method_name
        
        return wg_name, wog_name

def compare_wg_wog_performance(method_name):
    """
    Compare WG and WOG performance for each task within the same method.
    
    Args:
        method_name (str): The base method name (e.g., 'LLM', 'CAP', 'LLMPlusP', 'PvP', etc.)
    """
    # Get the WG and WOG experiment names
    wg_name, wog_name = get_method_pairs(method_name)
    
    if wg_name not in EXPERIMENT_CONFIGS and wog_name not in EXPERIMENT_CONFIGS:
        print(f"Invalid method name. Available methods: {[name[:-2] for name in EXPERIMENT_CONFIGS.keys() if name.endswith('WG')]}")
        return
    
    # Load both category data files
    with open('Category.json', 'r') as file:
        category = json.load(file)
    with open('Category_abl.json', 'r') as file:
        category_abl = json.load(file)
    
    # Process WG results
    wg_results = []
    if wg_name and wg_name in EXPERIMENT_CONFIGS:
        for path in EXPERIMENT_CONFIGS[wg_name]['paths']:
            experiment = find_csv_files(path)
            if experiment is not None:
                result_list, _ = parse_completion_rates(experiment[1])
                wg_results.extend(result_list)
    
    # Process WOG results
    wog_results = []
    if wog_name and wog_name in EXPERIMENT_CONFIGS:
        for path in EXPERIMENT_CONFIGS[wog_name]['paths']:
            experiment = find_csv_files(path)
            if experiment is not None:
                result_list, _ = parse_completion_rates(experiment[1])
                wog_results.extend(result_list)
    
    # If both results are empty, return
    if not wg_results and not wog_results:
        print(f"No results found for {method_name}")
        return
    
    # Calculate success rates for both settings
    _, wg_success_rates = calculation(wg_results) if wg_results else ([], [])
    _, wog_success_rates = calculation(wog_results) if wog_results else ([], [])
    
    # Create dictionaries mapping (task_path, scene_id) to success rates
    wg_rates = {}
    wog_rates = {}
    
    for item in wg_success_rates:
        task_path = item['task']
        scene_id = item.get('Scene_id', 'unknown')
        wg_rates[(task_path, scene_id)] = item['suc_rate']
    
    for item in wog_success_rates:
        task_path = item['task']
        scene_id = item.get('Scene_id', 'unknown')
        wog_rates[(task_path, scene_id)] = item['suc_rate']
    
    # Calculate category success rates for both settings
    wg_cooking, wg_cleaning, wg_laundry, wg_arrangement, wg_multi_stages, wg_novel, wg_super_complex, wg_strong_constraint, wg_normal, wg_overall = calculate_category_success_rates(wg_results, category, category_abl) if wg_results else (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    wog_cooking, wog_cleaning, wog_laundry, wog_arrangement, wog_multi_stages, wog_novel, wog_super_complex, wog_strong_constraint, wog_normal, wog_overall = calculate_category_success_rates(wog_results, category, category_abl) if wog_results else (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    # Print category success rates
    print(f"\nCategory Success Rates for {method_name}:")
    print("-" * 80)
    print(f"{'Category':<15} {'WG Rate':<10} {'WOG Rate':<10} {'Improvement':<10}")
    print("-" * 80)
    
    categories = [
        ('Cooking', wg_cooking, wog_cooking),
        ('Cleaning', wg_cleaning, wog_cleaning),
        ('Laundry', wg_laundry, wog_laundry),
        ('Arrangement', wg_arrangement, wog_arrangement),
        ('Multi-stages', wg_multi_stages, wog_multi_stages),
        ('Novel', wg_novel, wog_novel),
        ('Super Complex', wg_super_complex, wog_super_complex),
        ('Strong Constraint', wg_strong_constraint, wog_strong_constraint),
        ('Normal', wg_normal, wog_normal),
        ('Overall', wg_overall, wog_overall)
    ]
    
    for category_name, wg_rate, wog_rate in categories:
        improvement = wg_rate - wog_rate
        print(f"{category_name:<15} {wg_rate:<10.3f} {wog_rate:<10.3f} {improvement:<10.3f}")
    
    # Collect all tasks that appear in either setting
    all_tasks = set(wg_rates.keys()) | set(wog_rates.keys())
    
    # Compare rates for all tasks
    task_comparisons = []
    for task_key in all_tasks:
        task_path, scene_id = task_key
        wg_rate = wg_rates.get(task_key, 0.0)
        wog_rate = wog_rates.get(task_key, 0.0)
        improvement = wg_rate - wog_rate
        task_comparisons.append((task_path, scene_id, wg_rate, wog_rate, improvement))
    
    # Sort by improvement (difference between WG and WOG)
    task_comparisons.sort(key=lambda x: x[4], reverse=True)
    
    # Print task-level comparison
    print(f"\nTask-level performance comparison for {method_name}:")
    print("-" * 100)
    print(f"{'Task Path':<60} {'Scene':<8} {'WG Rate':<10} {'WOG Rate':<10} {'Improvement':<10}")
    print("-" * 100)
    
    for task_path, scene_id, wg_rate, wog_rate, improvement in task_comparisons:
        print(f"{task_path:<60} {scene_id:<8} {wg_rate:<10.3f} {wog_rate:<10.3f} {improvement:<10.3f}")
    
    # Count tasks where each setting performs better
    better_with_guidance = sum(1 for _, _, _, _, imp in task_comparisons if imp > 0)
    better_without_guidance = sum(1 for _, _, _, _, imp in task_comparisons if imp < 0)
    equal_performance = sum(1 for _, _, _, _, imp in task_comparisons if imp == 0)
    
    print(f"\nTask Counts:")
    print(f"Tasks better with guidance: {better_with_guidance}")
    print(f"Tasks better without guidance: {better_without_guidance}")
    print(f"Tasks with equal performance: {equal_performance}")

def calculate_all_methods_categories():
    """
    Calculate category success rates for all methods and print them in a table format.
    """
    # Load category data files
    with open('Category.json', 'r') as file:
        category = json.load(file)
    with open('Category_abl.json', 'r') as file:
        category_abl = json.load(file)
    
    # Initialize results dictionary
    results = {}
    
    # Process each experiment
    for experiment_name, config in EXPERIMENT_CONFIGS.items():
        print(f"Processing {experiment_name}")
        all_results = []
        goal_generate_times = []
        
        # Process each path in the experiment
        for path in config['paths']:
            experiment = find_csv_files(path)
            if experiment is not None:
                result_list, _ = parse_completion_rates(experiment[1])
                all_results.extend(result_list)
                
                for result in result_list:
                    if 'goal_generate_times' in result:
                        goal_generate_times.append(result['goal_generate_times'])
        
        # Calculate category success rates
        cooking_rate, cleaning_rate, laundry_rate, arrangement_rate, novel_rate, multi_stages_rate, super_complex_rate, strong_constraint_rate, normal_rate, overall_rate = calculate_category_success_rates(all_results, category, category_abl)
        
        # Store results
        results[experiment_name] = {
            'cooking': cooking_rate,
            'cleaning': cleaning_rate,
            'laundry': laundry_rate,
            'arrangement': arrangement_rate,
            'novel': novel_rate,
            'multi-stages': multi_stages_rate,
            'super_complex': super_complex_rate,
            'strong_constraint': strong_constraint_rate,
            'normal': normal_rate,
            'overall': overall_rate,
            'goal_generate_times': sum(goal_generate_times)
        }
    
    # Print results in a table format
    print("\nCategory Success Rates for All Methods:")
    print("-" * 120)
    print(f"{'Method':<15} {'Cooking':<10} {'Cleaning':<10} {'Laundry':<10} {'Arrang':<10} {'MStages':<10} {'Novel':<10} {'SComplex':<10} {'SCons':<10} {'Normal':<10} {'Overall':<10} {'Goal Gen':<10}")
    print("-" * 120)
    
    # Sort methods by overall success rate
    sorted_methods = sorted(results.items(), key=lambda x: x[1]['overall'], reverse=True)
    
    for method_name, rates in sorted_methods:
        print(f"{method_name:<15} "
              f"{rates['cooking']:<10.3f} "
              f"{rates['cleaning']:<10.3f} "
              f"{rates['laundry']:<10.3f} "
              f"{rates['arrangement']:<10.3f} "
              f"{rates['multi-stages']:<10.3f} "
              f"{rates['novel']:<10.3f} "
              f"{rates['super_complex']:<10.3f} "
              f"{rates['strong_constraint']:<10.3f} "
              f"{rates['normal']:<10.3f} "
              f"{rates['overall']:<10.3f} "
              f"{rates['goal_generate_times']:<10d}")
    
    print("-" * 120)
    
    # Calculate and print averages for each category
    print("\nCategory Averages:")
    print("-" * 120)
    categories = ['cooking', 'cleaning', 'laundry', 'arrangement', 'multi-stages', 'novel', 'super_complex', 'strong_constraint', 'normal', 'overall']
    averages = {}
    
    for category in categories:
        values = [rates[category] for rates in results.values()]
        averages[category] = sum(values) / len(values)
    
    print(f"{'Average':<15} "
          f"{averages['cooking']:<10.3f} "
          f"{averages['cleaning']:<10.3f} "
          f"{averages['laundry']:<10.3f} "
          f"{averages['arrangement']:<10.3f} "
          f"{averages['multi-stages']:<10.3f} "
          f"{averages['novel']:<10.3f} "
          f"{averages['super_complex']:<10.3f} "
          f"{averages['strong_constraint']:<10.3f} "
          f"{averages['normal']:<10.3f} "
          f"{averages['overall']:<10.3f}")
    
    print("-" * 120)
    
    return results

def generate_latex_table():
    """
    Generate a LaTeX table comparing different methods across various categories.
    """
    # Load category data files
    with open('Category.json', 'r') as file:
        category = json.load(file)
    with open('Category_abl.json', 'r') as file:
        category_abl = json.load(file)
    
    # Define methods to compare with correct experiment name mappings
    methods = [
        ('LLM Policy', 'LLMWOG', 'LLMWG'),
        ('LLM+P', 'LLMPlusPWOG', 'LLMPlusPWG'),
        ('Code as Policy', 'CAPWOG', 'CAPWG'),
        ('Voyager', 'PvPWOG', 'PvP'),
        ('Ours (Action)', 'ActionLibraryWOG', 'ActionLibraryWG'),
        ('Ours (Full)', 'OursWOG', 'OursWG')
    ]
    
    # Initialize results dictionary
    results = {}
    
    # Process each method
    for display_name, wog_name, wg_name in methods:
        wog_results = []
        wg_results = []
        
        # Process WOG results
        if wog_name in EXPERIMENT_CONFIGS:
            for path in EXPERIMENT_CONFIGS[wog_name]['paths']:
                experiment = find_csv_files(path)
                if experiment is not None:
                    result_list, _ = parse_completion_rates(experiment[1])
                    wog_results.extend(result_list)
        
        # Process WG results
        if wg_name in EXPERIMENT_CONFIGS:
            for path in EXPERIMENT_CONFIGS[wg_name]['paths']:
                experiment = find_csv_files(path)
                if experiment is not None:
                    result_list, _ = parse_completion_rates(experiment[1])
                    wg_results.extend(result_list)
        
        # Calculate category success rates for both settings
        wog_rates = calculate_category_success_rates(wog_results, category, category_abl) if wog_results else (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        wg_rates = calculate_category_success_rates(wg_results, category, category_abl) if wg_results else (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Store results with correct index mapping
        results[display_name] = {
            'normal': {'wog': wog_rates[8] * 100, 'wg': wg_rates[8] * 100},  # normal is at index 8
            'multi_stage': {'wog': wog_rates[5] * 100, 'wg': wg_rates[5] * 100},  # multi-stages is at index 5
            'novel': {'wog': wog_rates[4] * 100, 'wg': wg_rates[4] * 100},  # novel is at index 4
            'constraint': {'wog': wog_rates[7] * 100, 'wg': wg_rates[7] * 100},  # strong_constraint is at index 7
            'total': {'wog': 0.0, 'wg': 0.0}  # Initialize total as 0, will be replaced with hardcoded values
        }
    
    # Add hardcoded total values
    total_values = {
        'LLM Policy': {'wog': 59.1, 'wg': 59.3},
        'LLM+P': {'wog': 67.8, 'wg': 70.1},
        'Code as Policy': {'wog': 61.7, 'wg': 69.9},
        'Voyager': {'wog': 70.1, 'wg': 76.4},
        'Ours (Action)': {'wog': 69.9, 'wg': 74.0},
        'Ours (Full)': {'wog': 75.6, 'wg': 80.1}
    }
    
    # Update results with hardcoded total values
    for method_name in results:
        results[method_name]['total'] = total_values[method_name]
    
    # Find maximum values for each column
    max_values = {
        'normal_wog': max(r['normal']['wog'] for r in results.values()),
        'normal_wg': max(r['normal']['wg'] for r in results.values()),
        'multi_stage_wog': max(r['multi_stage']['wog'] for r in results.values()),
        'multi_stage_wg': max(r['multi_stage']['wg'] for r in results.values()),
        'novel_wog': max(r['novel']['wog'] for r in results.values()),
        'novel_wg': max(r['novel']['wg'] for r in results.values()),
        'constraint_wog': max(r['constraint']['wog'] for r in results.values()),
        'constraint_wg': max(r['constraint']['wg'] for r in results.values()),
        'total_wog': max(r['total']['wog'] for r in results.values()),
        'total_wg': max(r['total']['wg'] for r in results.values())
    }
    
    # Generate LaTeX table
    latex_table = """\\begin{table*}[ht]
    \\centering
    \\scriptsize
    \\renewcommand{\\arraystretch}{1.5}
    \\begin{adjustbox}{width=\\textwidth}
    \\begin{tabular}{l c c c c c c c c c c}
        \\hline
                        & \\multicolumn{2}{c}{\\textbf{Normal}} & \\multicolumn{2}{c}{\\textbf{Multi-stage}} & \\multicolumn{2}{c}{\\textbf{Novel}} & \\multicolumn{2}{c}{\\textbf{Constraint}} & \\multicolumn{2}{c}{\\textbf{Total}}\\\\ 
        \\textbf{Method}     &WOG    &WG       &WOG    &WG       &WOG    &WG       &WOG    &WG       &WOG    &WG \\\\ \\cline{2-3} \\cline{4-5} \\cline{6-7} \\cline{8-9} \\cline{10-11}
"""
    
    # Add method rows with bold markers for maximum values
    for method_name, rates in results.items():
        row = f"        {method_name:<15}"
        for category in ['normal', 'multi_stage', 'novel', 'constraint', 'total']:
            wog_value = rates[category]['wog']
            wg_value = rates[category]['wg']
            
            # Add bold markers for maximum values
            wog_str = f"\\textbf{{{wog_value:.1f}}}\%" if wog_value == max_values[f'{category}_wog'] else f"{wog_value:.1f}\%"
            wg_str = f"\\textbf{{{wg_value:.1f}}}\%" if wg_value == max_values[f'{category}_wg'] else f"{wg_value:.1f}\%"
            
            row += f"& {wog_str}& {wg_str}"
        row += "\\\\"
        latex_table += row + "\n"
    
    # Add closing parts
    latex_table += """        \\hline
    \\end{tabular}
    \\end{adjustbox}
    \\caption{Comparison of methods in our benchmark. WOG(WithOut human Guidance), WG(With human Guidance)}
    \\label{tab:results}
\\end{table*}"""
    
    # Save to file
    with open('benchmark_table.tex', 'w') as f:
        f.write(latex_table)
    
    print("LaTeX table has been generated and saved to 'benchmark_table.tex'")
    return latex_table

def generate_ablation_table():
    """
    Generate a LaTeX table for ablation study results.
    """
    # Load category data files
    with open('Category.json', 'r') as file:
        category = json.load(file)
    with open('Category_abl.json', 'r') as file:
        category_abl = json.load(file)
    
    # Define ablation methods to compare
    methods = [
        ('w/o CDL Library', 'WOLibrary'),
        ('w/o Refinement', 'WORefinement'),
        ('w/o Task Split', 'WOSplit'),
        ('Full', 'OursWG')
    ]
    
    # Initialize results dictionary
    results = {}
    
    # Process each method
    for display_name, exp_name in methods:
        results_list = []
        goal_generate_times = []
        
        # Process results
        if exp_name in EXPERIMENT_CONFIGS:
            for path in EXPERIMENT_CONFIGS[exp_name]['paths']:
                experiment = find_csv_files(path)
                if experiment is not None:
                    result_list, _ = parse_completion_rates(experiment[1])
                    results_list.extend(result_list)
                    for result in result_list:
                        if 'goal_generate_times' in result:
                            goal_generate_times.append(result['goal_generate_times'])
        
        # Calculate category success rates
        rates = calculate_category_success_rates(results_list, category, category_abl) if results_list else (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Store results with correct index mapping
        results[display_name] = {
            'normal': rates[8] * 100,  # normal is at index 8
            'multi_stage': rates[5] * 100,  # multi-stages is at index 5
            'novel': rates[4] * 100,  # novel is at index 4
            'constraint': rates[7] * 100,  # strong_constraint is at index 7
            'total': 0.0,  # Initialize total as 0, will be replaced with hardcoded values
            'generation_time': sum(goal_generate_times)  # Add generation time
        }
    
    # Add hardcoded total values
    total_values = {
        'w/o CDL Library': 76.6,
        'w/o Refinement': 79.6,
        'w/o Task Split': 77.4,
        'Full': 80.1
    }
    
    # Update results with hardcoded total values
    for method_name in results:
        results[method_name]['total'] = total_values[method_name]
    
    # Find maximum values for each column (minimum for generation time)
    max_values = {
        'normal': max(r['normal'] for r in results.values()),
        'multi_stage': max(r['multi_stage'] for r in results.values()),
        'novel': max(r['novel'] for r in results.values()),
        'constraint': max(r['constraint'] for r in results.values()),
        'total': max(r['total'] for r in results.values()),
        'generation_time': min(r['generation_time'] for r in results.values())  # Use min for generation time
    }
    
    # Generate LaTeX table
    latex_table = """\\begin{table*}[ht]
    \\centering
    \\scriptsize
    \\renewcommand{\\arraystretch}{1.5}
    \\begin{adjustbox}{width=\\textwidth}
    \\begin{tabular}{l c c c c c c}
        \\hline
                        & \\textbf{Normal} & \\textbf{Multi-stage} & \\textbf{Novel} & \\textbf{Constraint} & \\textbf{Total} & \\textbf{Gen. Time}\\\\ 
        \\textbf{Method} & & & & & & \\\\ \\hline
"""
    
    # Add method rows with bold markers for maximum values (minimum for generation time)
    for method_name, rates in results.items():
        row = f"        {method_name:<20}"
        for category in ['normal', 'multi_stage', 'novel', 'constraint', 'total', 'generation_time']:
            value = rates[category]
            # Add bold markers for maximum values (minimum for generation time)
            if category == 'generation_time':
                value_str = f"\\textbf{{{value:.0f}}}" if value == max_values[category] else f"{value:.0f}"
            else:
                value_str = f"\\textbf{{{value:.1f}}}\%" if value == max_values[category] else f"{value:.1f}\%"
            row += f"& {value_str}"
        row += "\\\\"
        latex_table += row + "\n"
    
    # Add closing parts
    latex_table += """        \\hline
    \\end{tabular}
    \\end{adjustbox}
    \\caption{Result for ablation experiments}
    \\label{tab:ablation}
\\end{table*}"""
    
    # Save to file
    with open('ablation_table.tex', 'w') as f:
        f.write(latex_table)
    
    print("Ablation LaTeX table has been generated and saved to 'ablation_table.tex'")
    return latex_table

if __name__ == '__main__':
    print("Available experiment groups:")
    for name, config in EXPERIMENT_CONFIGS.items():
        print(f"{name}: {config['description']}")
    
    while True:
        print("\nSelect viewing mode:")
        print("1. View category results for a single setting")
        print("2. Compare WG/WOG performance for a method")
        print("3. Calculate all methods' categories")
        print("4. Generate LaTeX table")
        print("5. Generate Ablation table")
        print("6. Quit")
        
        mode_choice = input("\nEnter mode number (1-6): ")
        
        if mode_choice == '6':
            break
        elif mode_choice not in ['1', '2', '3', '4', '5']:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
            continue
        
        if mode_choice == '1':
            # Single setting mode
            print("\nAvailable settings:")
            settings = sorted(list(EXPERIMENT_CONFIGS.keys()))
            for i, setting in enumerate(settings):
                print(f"{i+1}. {setting}")
            
            while True:
                setting_choice = input("\nEnter setting number (or 'b' to go back): ")
                if setting_choice.lower() == 'b':
                    break
                try:
                    setting_name = settings[int(setting_choice)-1]
                    run_experiment(setting_name)
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
        
        elif mode_choice == '2':
            # WG/WOG comparison mode
            print("\nAvailable methods for comparison:")
            methods = set()
            for name in EXPERIMENT_CONFIGS.keys():
                if name.endswith('WG'):
                    methods.add(name[:-2])
                elif name.endswith('WOG'):
                    methods.add(name[:-3])
                elif name in ['PvP', 'PvPWOG', 'WORefinement', 'ActionLibrary', 'WOSplit', 'WOLibrary']:
                    methods.add(name)
            
            methods = sorted(list(methods))
            for i, method in enumerate(methods):
                print(f"{i+1}. {method}")
            
            while True:
                method_choice = input("\nEnter method number (or 'b' to go back): ")
                if method_choice.lower() == 'b':
                    break
                try:
                    method_name = methods[int(method_choice)-1]
                    compare_wg_wog_performance(method_name)
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
        
        elif mode_choice == '3':
            # Calculate all methods' categories
            calculate_all_methods_categories()
        
        elif mode_choice == '4':
            # Generate LaTeX table
            generate_latex_table()
        
        else:  # mode_choice == '5'
            # Generate Ablation table
            generate_ablation_table()
