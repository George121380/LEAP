import pandas as pd
import re
import sys
sys.path.append('cdl_dataset/scripts')
from logic_parser import parse_logic_from_file_path
import json

def parse_completion_rates(csv_file_path):
    df = pd.read_csv(csv_file_path)
    result_list = []

    for index, row in df.iterrows():
        completion_rate = row['LLM Answer']
        debug_result = row['Debug Result']
        end_report = row['Goal Representation']


        task_path = row['Plan']

        if completion_rate=='1':
            result_dict = {
            'task_path': task_path,
            'keystate_completion_rate': True,
            'action_completion_rate': True,
            'success': True
        }
            result_list.append(result_dict)
            continue

        if debug_result=='Syntax Error':
            result_dict = {
            'task_path': task_path,
            'keystate_completion_rate': False,
            'action_completion_rate': False,
            'success': 'syntax error'
        }
            result_list.append(result_dict)
            continue

        if end_report=='Evaluation Finished':
            continue



        keystate_matches = re.findall(r'(Keystate: k\d+) - Completion Rate: ([\d.]+)', completion_rate)
        action_match = re.search(r'Action Completion Rate: ([\d.]+|No actions required)', completion_rate)

        keystate_dict = {}
        for keystate, completion_rate in keystate_matches:
            keystate_dict[keystate.replace('Keystate: ','')] = float(completion_rate)

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

def culculation(result_list):
    difficulty_dict = json.load(open('cdl_dataset/difficulty_counting.json'))
    success_rate_dict={}
    sum_success_rate = 0
    for entry in result_list:
        task_success_rate = 0
        task_path = entry['task_path']
        if task_path=='cdl_dataset/dataset/Put_groceries_in_Fridge/g4.txt':
            print('debug')
        if entry['success']=='syntax error':
            task_success_rate = 0
        if entry['success']:
            task_success_rate = 1
        
        else:
            if entry['keystate_completion_rate']=={}:
                task_success_rate = 0
                print('No keystate is recorded')
            else:
                solution_combination=parse_logic_from_file_path(task_path)
                if solution_combination == 'No keystate is needed':
                    task_success_rate = entry['action_completion_rate']

                else:
                    max_keystate_completion_rate = 0
                    dict_flag=True

                    for solution in solution_combination:
                        for keystate in solution:
                            assert keystate in entry['keystate_completion_rate']
                            if not task_path in difficulty_dict:
                                dict_flag=False
                                print(f'{task_path} not in difficulty_dict')
                                break
                            if not keystate in difficulty_dict[task_path]:
                                dict_flag=False
                                print(f'{keystate} not in difficulty_dict')
                                break
                            

                    for solution in solution_combination:
                        solution_steps_num=0
                        current_solution_keystate_completion_rate = 0

                        for keystate in solution:
                            if dict_flag:
                                keystate_steps_num = difficulty_dict[task_path][keystate]
                                solution_steps_num+=keystate_steps_num
                                current_solution_keystate_completion_rate+=entry['keystate_completion_rate'][keystate]*keystate_steps_num

                            else:
                                current_solution_keystate_completion_rate+=entry['keystate_completion_rate'][keystate]
                                solution_steps_num+=1
                    
                    
                    current_solution_keystate_completion_rate/=solution_steps_num
                    max_keystate_completion_rate = max(max_keystate_completion_rate, current_solution_keystate_completion_rate)
                
                if entry['action_completion_rate'] == 'No actions required':
                    task_success_rate = max_keystate_completion_rate

                else:
                    keystate_wight = 2
                    action_wight = 1
                    task_success_rate = (max_keystate_completion_rate * keystate_wight + entry['action_completion_rate'] * action_wight) / (keystate_wight + action_wight)
        
        success_rate_dict[entry['task_path']]=task_success_rate
        sum_success_rate+=task_success_rate
    
    avg_success_rate = sum_success_rate / len(success_rate_dict)
    return avg_success_rate, success_rate_dict

if __name__ == '__main__':
    # ours
    print('ours')
    print('='*80)
    csv_file_path1 = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/baseline_result/our_w_library_o_human/epoch_20241014_050122/epoch.csv'
    result = parse_completion_rates(csv_file_path1)
    avg_success_rate1, success_rate_list = culculation(result)
    csv_file_path2 = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/baseline_result/our_w_library_o_human/epoch_20241014_050123/epoch.csv'
    result = parse_completion_rates(csv_file_path2)
    avg_success_rate2, success_rate_list = culculation(result)
    csv_file_path3 = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/baseline_result/our_w_library_o_human/epoch_20241014_050125/epoch.csv'
    result = parse_completion_rates(csv_file_path3)
    avg_success_rate3, success_rate_list = culculation(result)

    av_avg_success_rate = (avg_success_rate1 + avg_success_rate2 ) / 2

    virance = ((avg_success_rate1 - av_avg_success_rate) ** 2 + (avg_success_rate2 - av_avg_success_rate) ** 2 ) / 2

    print('Average success rate:', av_avg_success_rate)
    print('Virance:', virance)


    print('LLMs')
    print('='*80)
    csv_file_path1 = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/baseline_result/LLM_o_library_o_human/epoch_20241013_232256/epoch.csv'
    result = parse_completion_rates(csv_file_path1)
    avg_success_rate1, success_rate_list = culculation(result)
    csv_file_path2 = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/baseline_result/LLM_o_library_o_human/epoch_20241013_234439/epoch.csv'
    result = parse_completion_rates(csv_file_path2)
    avg_success_rate2, success_rate_list = culculation(result)
    csv_file_path3 = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/baseline_result/LLM_o_library_o_human/epoch_20241013_234441/epoch.csv'
    result = parse_completion_rates(csv_file_path3)
    avg_success_rate3, success_rate_list = culculation(result)

    av_avg_success_rate = (avg_success_rate1 + avg_success_rate2 + avg_success_rate3) / 3

    virance = ((avg_success_rate1 - av_avg_success_rate) ** 2 + (avg_success_rate2 - av_avg_success_rate) ** 2 + (avg_success_rate3 - av_avg_success_rate) ** 2) / 3

    print('Average success rate:', av_avg_success_rate)
    print('Virance:', virance)

                
                        
                
            
