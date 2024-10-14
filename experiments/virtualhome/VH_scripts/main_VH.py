# from env_kitchen import Agent,KitchenEnvironment
import sys
import json
import re
sys.path.append('embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
sys.path.append('cdl_dataset/scripts')
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
import pdb
import os
from dataset import parse_file_to_json

init_path="experiments/virtualhome/CDLs/init_scene_PO.cdl"
dataset_folder_path='cdl_dataset/dataset'

import argparse
from tqdm import tqdm

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
    objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(init_scene_graph)
    construct_cdl(init_path,objects,states,relationships,properties,cat_statement)
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
    evaluator=Evaluator(task_path,logger,epoch_path)

    if args.model=='ours':
        ##test
        agent=VHAgent(args, init_path,logger,True,epoch_path)
        ##test_end
        all_behaviors_from_library=agent.download_behaviors_from_library()
        agent.set_human_helper(Human(init_scene_graph,guidance))
        # agent.set_initial_human_instruction(task_data['Goal'])
        agent.reset_goal(task_data['Goal'],classes,task_data['Task name'],First_time=True)#ini a GR

        # Human_Guidance=[]
        # for sub_goal in agent.sub_goal_list:
        #     question=re.sub(r'^\d+[\.\:]?\s*', '', sub_goal.lower())
        #     question="Can you tell me how to "+question
        #     answer=agent.query_human(question)
        #     Human_Guidance.append(answer)

    # return True
    if args.model=='LLM':
        agent = LLM_Agent(args, init_path,logger,epoch_path)
        agent.set_human_helper(Human(init_scene_graph,guidance))
        agent.reset_goal(task_data['Goal'],task_data['Task name'])#ini a GR
        agent.item_infoto_nl()
        # agent.act()
        # return


    if args.model=='LLM+P':
        pass

    if args.model=='CAP':
        pass

    env=VH_Env(init_scene_graph)
    while True:
        action,plan = agent.act() #Planning   
        if action=="human guided":
            continue 
        if action=="Failed" or action=='over':
            print("Task Path is: ",task_path)
            print("Task Goal is: ",task_data['Goal'])
            executed_actions=env.report_actions()
            evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
            if evaluation_result=="Keystate Evaluate Error":
                print("Keystate Evaluate Error")
                return False
            if action=='Failed':
                print("Task failed")
            if epoch_logger:
                task_summary_record(epoch_logger,task_data['Task name'],task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.exp_helper_query_times)
            return True
        
        print('Action: ',str(action))
        observation = env.step(action) #Execute action
        agent.updates(observation) #Update agent's state
        evaluator.updates(observation) #Update evaluator's state
        evaluation_result=evaluator.evaluate(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
        if evaluation_result:
            executed_actions=env.report_actions()
            print("Task Success")
            if epoch_logger:
                task_summary_record(epoch_logger,task_data['Task name'],task_data['Goal'],executed_actions,start_time,1,task_path,agent.exp_helper_query_times)
            return True

def test_evaluate(args):
    _,classes,init_scene_graph,guidance=load_scene()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger = setup_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Cook_some_food/g2.txt'
    run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph,guidance)


def evaluation(args):
    files=evaluation_task_loader(dataset_folder_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger = setup_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    files = tqdm(files, desc="Evaluating tasks")
    for task_file in files:
        try:
            _,classes,init_scene_graph,guidance=load_scene()
            task_path=os.path.join(dataset_folder_path,task_file)
            Debug=run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph,guidance)
            
        except Exception as e:
            print(e)
            epoch_logger.info(task_path,'Syntax Error',None,None,None,task_path)
            continue
    end_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger.info('Evaluation Finished',end_time,'','','','')

def check_evaluation(args):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    files=evaluation_task_loader(dataset_folder_path)
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    for task_file in files:
        task_path=os.path.join(dataset_folder_path,task_file)
        print(task_path)
        evaluator=Evaluator(task_path,epoch_logger,epoch_path)
    

def check_evaluation_single(args):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
   
    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Pet_cat/g2.txt'
    evaluator=Evaluator(task_path,epoch_logger,epoch_path)

if __name__ == '__main__':
    args = parse_args()
    # evaluation(args)
    # test_evaluate(args)
    check_evaluation(args)
    # check_evaluation_single(args)