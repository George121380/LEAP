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

from utils_eval import get_nodes_information,construct_cdl
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time
from logger import setup_logger
from human import Human
from evaluation import Evaluator
random.seed(time.time())
import os
from dataset import parse_file_to_json
from logic_parser import parse_logic_from_file_path

init_path="experiments/virtualhome/CDLs/init_scene_PO.cdl"
dataset_folder_path='cdl_dataset/dataset'

import argparse
from tqdm import tqdm

result_dict = {}

def parse_args():
    parser = argparse.ArgumentParser(description="Run an embodied agent evaluation.")    
    parser.add_argument('--llm_model', type=str, default='gpt-4o', 
                        help="Specify the LLM model to be used. gpt-4o, deepseek")
    parser.add_argument('--library_extraction', type=str,
                        help="Specify the library extraction method to be used.")
    parser.add_argument('--model', type=str,default='ours',
                        help="ours, LLM, LLM+P, CAP")
    parser.add_argument('--human_guidance', type=str, default=False,
                    help="Whether to use human guidance (True or False).")
    parser.add_argument('--use_library', type=bool, default=False,
                    help="Whether to use library (True or False).")

    return parser.parse_args()

def load_scene():
    scene_path='cdl_dataset/Scene.json'
    with open(scene_path) as f:
        scene=json.load(f)
    init_scene_graph = EnvironmentGraph(scene)
    guidance_path='cdl_dataset/human_guidancea_library.json'
    guidance=json.load(open(guidance_path))
    additional_information=''
    objects,states,relationships,properties,categories,classes,cat_statement, sizes=get_nodes_information(init_scene_graph)
    construct_cdl(init_path,objects,states,relationships,properties,cat_statement, sizes)
    return additional_information,classes,init_scene_graph,guidance

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
    logger = setup_logger(folder_path,timestamp=None,task_name=log_name)
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

        evaluator=Evaluator(task_path,logger,epoch_path)
        env=VH_Env(init_scene_graph)
        for key in combination:
            plan=evaluator.complete_single_keystate(key)
            result_dict[task_path][str(combination)][key]=len(plan)
            for action in plan:
                print('Action: ',str(action))
                observation = env.step(action) #Execute action
                evaluator.updates(observation) #Update evaluator's state
    json.dump(result_dict,open('result.json','w'),indent=4)
       

def counting(args):
    files=evaluation_task_loader(dataset_folder_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger = setup_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    files = tqdm(files, desc="Evaluating tasks")
    for task_file in files:
        _,classes,init_scene_graph,guidance=load_scene()
        task_path=os.path.join(dataset_folder_path,task_file)
        if task_path in result_dict:
            continue
        Debug=run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph,guidance)
    print(result_dict)
        
if __name__ == '__main__':
    args = parse_args()
    if os.path.exists('result.json'):
        with open('result.json') as f:
            result_dict=json.load(f)
    counting(args)