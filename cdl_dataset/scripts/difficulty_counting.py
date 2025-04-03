import csv
from collections import defaultdict
import re
import json

import sys
sys.path.append('cdl_dataset/scripts')
sys.path.append('experiments/virtualhome/VH_scripts')
sys.path.append('')
from datetime import datetime
from experiments.virtualhome.VH_scripts.agent import VHAgent
from experiments.virtualhome.VH_scripts.agent_LLM import LLM_Agent

from utils_eval import get_nodes_information,construct_cdl,load_config
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time
from logger import setup_task_logger
from evaluation import Evaluator
random.seed(time.time())
import os
from dataset import parse_file_to_json
from logic_parser import parse_logic_from_file_path
import yaml 
init_path="experiments/virtualhome/CDLs/init_scene_PO.cdl"
dataset_folder_path='cdl_dataset/dataset'
# dataset_folder_path='cdl_dataset/cooking'

from types import SimpleNamespace
import argparse
from tqdm import tqdm


from configs import OursWG, OursWOG, LLMWG, LLMWOG, LLMPlusPWG, LLMPlusPWOG, CAPWG, CAPWOG, load_scene, set_agent

sys.setrecursionlimit(1000000)

#################################################
#######          Select Configs           #######
#################################################

# config = OursWG()
# config = OursWOG()
config = LLMWG()
# config = LLMWOG()
# config = LLMPlusPWG()
# config = LLMPlusPWOG()
# config = CAPWG()
# config = CAPWOG()

#################################################

result_dict = {}

def load_scene(scene_id):
    scene_path=f'cdl_dataset/scenes/Scene_{scene_id}.json'
    with open(scene_path) as f:
        scene=json.load(f)
    init_scene_graph = EnvironmentGraph(scene)
    additional_information=''
    objects,states,relationships,properties,categories,classes,cat_statement, sizes=get_nodes_information(init_scene_graph)
    construct_cdl(init_path,objects,states,relationships,properties,cat_statement, sizes)
    return additional_information,classes,init_scene_graph

def evaluation_task_loader(dataset_folder_path):
    all_files=[]
    subdirs = [d for d in os.listdir(dataset_folder_path) if os.path.isdir(os.path.join(dataset_folder_path, d))]
    for subdir in subdirs:
        subdir_path = os.path.join(dataset_folder_path, subdir)
        files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
        for file in files:
            if not 'bug' in file:
                all_files.append(os.path.join(subdir,file))
    # subdir_path = os.path.join(dataset_folder_path, selected_subdir)
    # files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
    return all_files

def task_summary_record(epoch_logger,task_name,goal,action_history,start_time,complete_rate,task_path,exp_helper_query_times):
    current_time = time.time()
    time_elapsed=''
    if start_time:
        time_elapsed = current_time - start_time
    time_info=f'Time consume: {int(time_elapsed)} seconds'
    time_info+=f'\nExp_helper query times: {str(exp_helper_query_times)}'
    epoch_logger.info(task_name,goal,action_history,time_info,complete_rate,task_path)
    # pass
    
def run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph,guidance):
    start_time = time.time()
    c=os.path.basename(os.path.dirname(task_path))
    g_index=os.path.basename(task_path).replace('.txt','')
    log_name=c+'_'+g_index

    folder_path = f'log/epoch_{timestamp}/records'
    epoch_path = f'log/epoch_{timestamp}'
    logger = setup_task_logger(folder_path,task_name=log_name)
    task_data=parse_file_to_json(task_path)
    print('='*60)
    print("Task Path is: ",task_path)
    print("Task Goal is: ",task_data['Goal'])
    print('='*60)
    keystates_combination=parse_logic_from_file_path(task_path)
    result_dict[task_path] = {}
    if keystates_combination=='No keystate is needed':
        return
    for combination in keystates_combination:
        result_dict[task_path][str(combination)]={}

        evaluator=Evaluator(args,task_path,logger,epoch_path)
        current_graph=init_scene_graph.copy()
        env=VH_Env(current_graph)
        for key in combination:
            plan=evaluator.complete_single_keystate(key)
            result_dict[task_path][str(combination)][key]=len(plan)
            for action in plan:
                # print("#"*60)
                print('Action: ',str(action))
                if "open" in str(action):
                    print("debug")
                observation = env.step(action) #Execute action
                # print(env.find_room(2069))
                # print(env.get_visible_list())
                # print("#"*60)

                if 'You can not' in observation:
                    print(observation)
                    raise Exception('Syntax Error')
                evaluator.updates(observation) #Update evaluator's state
    json.dump(result_dict,open(f'result_{args.scene_id}.json','w'),indent=4)
       

def counting(args, task_path=None):
    """
    Count the difficulty of tasks.
    
    Args:
        args: Configuration arguments
        task_path (str, optional): Path to a specific task to count. If None, counts all tasks.
    """
    if task_path:
        # Count single task
        print(f"Counting difficulty for task: {task_path}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        epoch_logger = setup_task_logger(f'log/epoch_{timestamp}')
        _, classes, init_scene_graph = load_scene(args.scene_id)
        run(args, epoch_logger, timestamp, task_path, classes, init_scene_graph, None)
    else:
        # Count all tasks
        files = evaluation_task_loader(dataset_folder_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        epoch_logger = setup_task_logger(f'log/epoch_{timestamp}')
        files = tqdm(files, desc="Evaluating tasks")
        for task_file in files:
            _, classes, init_scene_graph = load_scene(args.scene_id)
            task_path = os.path.join(dataset_folder_path, task_file)
            if task_path in result_dict:
                continue
            run(args, epoch_logger, timestamp, task_path, classes, init_scene_graph, None)
    
    print(result_dict)
        
if __name__ == '__main__':
    # Interactive input for scene selection
    print("\nAvailable scenes:")
    scenes = [f for f in os.listdir('cdl_dataset/scenes') if f.startswith('Scene_')]
    for i, scene in enumerate(scenes):
        print(f"{i+1}. {scene}")
    
    while True:
        try:
            scene_idx = int(input("\nPlease select a scene number (1-{}): ".format(len(scenes)))) - 1
            if 0 <= scene_idx < len(scenes):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    config.scene_id = scene_idx
    
    # Load existing results if available
    if os.path.exists(f'result_{config.scene_id}.json'):
        with open(f'result_{config.scene_id}.json') as f:
            result_dict = json.load(f)
    
    # Interactive input for task selection
    print("\nTask selection options:")
    print("1. Count all tasks")
    print("2. Count a specific task")
    
    while True:
        try:
            choice = int(input("\nPlease select an option (1-2): "))
            if choice in [1, 2]:
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    task_path = None
    if choice == 2:
        # Show available tasks
        print("\nAvailable tasks:")
        files = evaluation_task_loader(dataset_folder_path)
        for i, file in enumerate(files):
            print(f"{i+1}. {file}")
        
        while True:
            try:
                task_idx = int(input("\nPlease select a task number (1-{}): ".format(len(files)))) - 1
                if 0 <= task_idx < len(files):
                    task_path = os.path.join(dataset_folder_path, files[task_idx])
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    counting(config, task_path)