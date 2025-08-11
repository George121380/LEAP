# ----------------------------------------------
# Main 
# ----------------------------------------------


import sys
import json
sys.path.append('../VirtualHome-HG/scripts')
sys.path.append('')
from datetime import datetime
from utils_eval import CrowControllerApplier, load_config, evaluation_task_loader, namespace_to_dict
from env import VH_Env
import random
import time
from logger import setup_task_logger, setup_epoch_logger, get_last_task_path_from_logger, filter_tasks

from evaluation import Evaluator
random.seed(time.time())
import yaml 
import os
from dataset import parse_file_to_json
from tqdm import tqdm
import shutil
from configs import OursWG, OursWOG, LLMWG, LLMWOG, LLMPlusPWG, LLMPlusPWOG, CAPWG, CAPWOG, WOLibrary, ActionLibrary, WORefinement, WOSplit, PvP, load_scene, set_agent
DATASET_FOLDER_PATH = 'VirtualHome-HG/dataset'

sys.setrecursionlimit(1000000)


running_mode='test' # Set default running mode to test

def print_task_info(task_data, scene_id):
    print('-'*60)
    print("Task Path is: ",task_data['task_path'])
    print("Task Goal is: ",task_data['Goal'])
    print("Scene ID is: ",scene_id)
    print("Possible Guidance: ",task_data['Guidance'])
    print('-'*60)

def task_summary_record(epoch_logger, task_logger, scene_id, goal, action_history, start_time, complete_rate, task_path, final_info):
    """
    Record the summary of a task execution.
    """
    current_time = time.time()
    if action_history == None:
        action_history = []
    time_elapsed = int(current_time - start_time) if start_time else ''
    time_info = f"Time consume: {time_elapsed} seconds\nExp_helper query times: {final_info['exp_helper_query_times']}\nGuidance query times: {final_info['guidance_query_times']}\nlibrary scale: {final_info['library_scale']}\ngoal generate times: {final_info['goal_generate_times']}\ngoal correct times: {final_info['goal_correct_times']}\naction_num: {len(action_history)}\n"
    epoch_logger.info(task_path, goal, action_history, time_info, complete_rate, f"Scene_id: {str(scene_id)}")
    task_logger.info("Task Summary:\nTask Goal:\n"+goal+"\nAction History:\n"+str(action_history)+"\nTime info:\n"+time_info+"\nTask complete rate:\n"+str(complete_rate)+"\n"+f"Scene_id: {str(scene_id)}")
    
def run(config,epoch_logger,epoch_path,task_path,classes,init_scene_graph):
    """
    Execute a single task with the specified agent.
    """
    start_time = time.time()
    log_name = f"{os.path.basename(os.path.dirname(task_path))}_{os.path.basename(task_path).replace('.txt', '')}_scene_{config.scene_id}"
    folder_path = f'{epoch_path}/records'
    # Set the task logger
    task_logger = setup_task_logger(folder_path, task_name = log_name)

    task_data=parse_file_to_json(task_path)

    task_goal=input("Please input the task goal: ")
    task_data['Goal']=task_goal

    print_task_info(task_data, config.scene_id)
    evaluator=Evaluator(config, task_path, task_logger, epoch_path)
    agent = set_agent(config, init_scene_graph, task_data, classes, task_logger, epoch_path)
    env=VH_Env(init_scene_graph)
    while True:
        try:
            action, plan = agent.act() # Planning 
            if action=="human guided":
                continue 
            if action=="Failed":
                print_task_info(task_data, config.scene_id)
                executed_actions=env.report_actions()
                evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
                if evaluation_result=="Keystate Evaluate Error":
                    print("Keystate Evaluate Error")
                    return False
                print("Task failed")
                if epoch_logger:
                    task_summary_record(epoch_logger,task_logger,config.scene_id,task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.final_important_numbers_report())
                return True
            
            if action=='over':
                print_task_info(task_data, config.scene_id)
                executed_actions=env.report_actions()
                evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
                if evaluation_result=="Keystate Evaluate Error":
                    print("Keystate Evaluate Error")
                    return False
                
                if evaluation_result:
                    print("Task Success")
                    if config.library: # Lift the behaviors if the library is used
                        agent.lift_behaviors()
                    if epoch_logger:
                        task_summary_record(epoch_logger,task_logger,config.scene_id,task_data['Goal'],executed_actions,start_time,1,task_path,agent.final_important_numbers_report())
                    return True
                else:
                    # Task is incomplete
                    if epoch_logger:
                        task_summary_record(epoch_logger,task_logger,config.scene_id,task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.final_important_numbers_report())
                return True
            
            print('Action: ',str(action))
            observation = env.step(action) #Execute action
            agent.updates(observation) #Update agent's state
            evaluator.updates(observation) #Update evaluator's state
            if not 'obs' in action.name and not 'exp' in action.name:
                evaluation_result=evaluator.evaluate(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
                
        except Exception as e:
            print_task_info(task_data, config.scene_id)
            print("Error happend in the execution")
            print(str(e))
            task_logger.info("Error record: "+str(e))
            evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
            executed_actions=env.report_actions()
            task_summary_record(epoch_logger,task_logger,config.scene_id,'Syntax Error',executed_actions,start_time,complete_rate,task_path,agent.final_important_numbers_report())
            return False
       

#################################################
#######          Main Functions           #######
#################################################

    
def evaluate_single(config):
    start_time = time.time()
    config.scene_id = 0
    # random choose a task
    task_path='VirtualHome-HG/dataset/Drink/g4.txt'
    # check existance of the task path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_path = f'log/{timestamp}_{config.logger_name}'
    epoch_logger = setup_epoch_logger(f'log/{timestamp}_{config.logger_name}')
    classes,init_scene_graph=load_scene(config.scene_id, epoch_path)
    run(config,epoch_logger,epoch_path,task_path,classes,init_scene_graph)
    
    end_time = time.time()
    print('Time Consumed: ',end_time-start_time)

if __name__ == '__main__':

    config = WOSplit()
    evaluate_single(config)