import sys
import json
import re
sys.path.append('cdl_dataset/scripts')
sys.path.append('')
from datetime import datetime
from experiments.virtualhome.VH_scripts.agent import VHAgent
from experiments.virtualhome.VH_scripts.agent_LLM import LLM_Agent
from utils_eval import get_nodes_information,construct_cdl, CrowControllerApplier, load_config, evaluation_task_loader
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time
from logger import setup_task_logger, setup_epoch_logger
from human import Human
from evaluation import Evaluator
random.seed(time.time())
import pdb
import yaml 
import os
from dataset import parse_file_to_json
from tqdm import tqdm

INIT_PATH_PO = "experiments/virtualhome/CDLs/init_scene_PO.cdl"
INIT_PATH_NPO = "experiments/virtualhome/CDLs/init_scene_NPO.cdl"
DATASET_FOLDER_PATH = 'cdl_dataset/dataset'
running_mode='debug' #debug or test 

def load_scene(scene_id):
    """
    Load a predefined scene based on its ID.
    """
    scene_path=f'cdl_dataset/scenes/Scene_{scene_id}.json'
    with open(scene_path) as f:
        scene=json.load(f)
    init_scene_graph = EnvironmentGraph(scene)

    # Generate CDL for NPO
    objects,states,relationships,properties,categories,classes,cat_statement,sizes=get_nodes_information(init_scene_graph,PO=False)
    construct_cdl(INIT_PATH_NPO,objects,states,relationships,properties,cat_statement,sizes)

    # Generate CDL for PO
    objects,states,relationships,properties,categories,classes,cat_statement,sizes=get_nodes_information(init_scene_graph)
    construct_cdl(INIT_PATH_PO,objects,states,relationships,properties,cat_statement,sizes)
    return classes,init_scene_graph

def task_summary_record(epoch_logger, task_name, goal, action_history, start_time, complete_rate, task_path, exp_helper_query_times):
    """
    Record the summary of a task execution.
    """
    current_time = time.time()
    time_elapsed = int(current_time - start_time) if start_time else ''
    time_info = f"Time consume: {time_elapsed} seconds\nExp_helper query times: {exp_helper_query_times}"
    epoch_logger.info(task_name, goal, action_history, time_info, complete_rate, task_path)
    
def run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph):
    """
    Execute a single task with the specified agent.
    """
    start_time = time.time()
    log_name = f"{os.path.basename(os.path.dirname(task_path))}_{os.path.basename(task_path).replace('.txt', '')}"
    folder_path = f'log/epoch_{timestamp}/records'
    epoch_path = f'log/epoch_{timestamp}'

    # Set the task logger
    task_logger = setup_task_logger(folder_path,timestamp=None,task_name=log_name)

    task_data=parse_file_to_json(task_path)
    evaluator=Evaluator(args,task_path,task_logger,epoch_path)

    # Setup agent based on the model type
    if args.model=='ours':
        args.agent_type='Planning'
        agent = VHAgent(
            args=args, 
            filepath=INIT_PATH_PO, 
            task_logger=task_logger, 
            PO=True, 
            epoch_path=epoch_path
        )
        agent.download_behaviors_from_library()
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],classes,task_data['Task name'],First_time=True)#ini a GR
    if args.model=='LLM':
        agent = LLM_Agent(
            args=args,
            filepath=INIT_PATH_PO,
            task_logger=task_logger,
            epoch_path=epoch_path
        )
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],task_data['Task name'])#ini a GR
        agent.item_infoto_nl()
    if args.model=='LLM+P':
        pass

    if args.model=='CAP':
        args.agent_type='Policy'
        agent = VHAgent(
            args=args, 
            filepath=INIT_PATH_PO, 
            task_logger=task_logger, 
            PO=True, 
            epoch_path=epoch_path
        )
        agent.download_behaviors_from_library()
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],classes,task_data['Task name'],First_time=True)#ini a GR

    ######## Test Human Guidance ########
    Human_Guidance=[]
    for sub_goal in agent.sub_goal_list:
        question=re.sub(r'^\d+[\.\:]?\s*', '', sub_goal.lower())
        question="Can you tell me how to "+question
        print("#"*80)
        print(question)
        print("#"*80)
        answer=agent.query_LLM_human(question)
        Human_Guidance.append(answer)
    ######## Test Human Guidance ########

    env=VH_Env(init_scene_graph)

    while True:
        action,plan = agent.act() #Planning   
        if action=="human guided":
            continue 
        if action=="Failed":
            print("Task Path is: ",task_path)
            print("Task Goal is: ",task_data['Goal'])
            executed_actions=env.report_actions()
            evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
            if evaluation_result=="Keystate Evaluate Error":
                print("Keystate Evaluate Error")
                return False
            print("Task failed")
            if epoch_logger:
                task_summary_record(epoch_logger,task_data['Task name'],task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.exp_helper_query_times)
            return True
        
        if action=='over':
            print("Task Path is: ",task_path)
            print("Task Goal is: ",task_data['Goal'])
            executed_actions=env.report_actions()
            evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
            if evaluation_result=="Keystate Evaluate Error":
                print("Keystate Evaluate Error")
                return False
            
            if evaluation_result:
                print("Task Success")
                if epoch_logger:
                    task_summary_record(epoch_logger,task_data['Task name'],task_data['Goal'],executed_actions,start_time,1,task_path,agent.exp_helper_query_times)
                return True
            else:
                if args.human_check_eventually:
                    action="human guided"
                    agent.final_human_check()
                    continue

                if epoch_logger:
                    task_summary_record(epoch_logger,task_data['Task name'],task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.exp_helper_query_times)
            return True
        
        print('Action: ',str(action))
        observation = env.step(action) #Execute action
        agent.updates(observation) #Update agent's state
        evaluator.updates(observation) #Update evaluator's state
        if not 'obs' in action.name and not 'exp' in action.name:
            evaluation_result=evaluator.evaluate(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
        # if evaluation_result:
        #     executed_actions=env.report_actions()
        #     print("Task Success")
        #     if epoch_logger:
        #         task_summary_record(epoch_logger,task_data['Task name'],task_data['Goal'],executed_actions,start_time,1,task_path,agent.exp_helper_query_times)
        #     return True

def evaluate_single(args):
    start_time = time.time()
    # print('Start Time: ',start_time)
    classes,init_scene_graph=load_scene(args.scene_id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    task_path='cdl_dataset/dataset/Wash_clothes/g1.txt'
    run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph)
    # test_simulator(init_scene_graph)
    end_time = time.time()
    # print('End Time: ',end_time)
    print('Time Consumed: ',end_time-start_time)

def evaluate_all(args): # main function
    files=evaluation_task_loader(DATASET_FOLDER_PATH)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Set logger and save configs
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    with open(f'log/epoch_{timestamp}/args.yaml', 'w') as file:
        yaml.dump(vars(args), file)
    
    files = tqdm(files, desc="Evaluating tasks")
    for task_file in files:

        if running_mode=='debug':
            classes,init_scene_graph=load_scene(args.scene_id)
            task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
            Debug=run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph)
            
        if running_mode=='test':
            try:
                classes,init_scene_graph=load_scene(args.scene_id)
                task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
                Debug=run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph)
            except Exception as e:
                print(e)
                epoch_logger.info(task_path,'Syntax Error',None,None,None,task_path)
                continue

    end_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger.info('Evaluation Finished',end_time,'','','','')

def check_task_define_all(args):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    files=evaluation_task_loader(DATASET_FOLDER_PATH)
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    for task_file in files:
        task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
        print(task_path)
        evaluator=Evaluator(args,task_path,epoch_logger,epoch_path)
        evaluator.left_action_counting_for_each_keystate()



def check_task_define_single(args):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
   
    task_path='cdl_dataset/dataset/Drink/g2.txt'
    evaluator=Evaluator(args,task_path,epoch_logger,epoch_path)
    evaluator.left_action_counting_for_each_keystate()

def case_study_easy2hard(args): # main function

    task_combination_1=['Prepare_breakfast/g4.txt']
    # task_combination_1=['Prepare_breakfast/g3.txt','Prepare_breakfast/g4.txt']


    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    with open(f'log/epoch_{timestamp}/args.yaml', 'w') as file:
        yaml.dump(vars(args), file)
    combination_1 = tqdm(task_combination_1, desc="Evaluating tasks")
    for task_file in combination_1:
            classes,init_scene_graph=load_scene(args.scene_id)
            task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
            Debug=run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph)
    end_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger.info('Evaluation Finished',end_time,'','','','')


def test_simulator(init_scene_graph):
    """
    Give a list of actions, test the simulator
    """
    env=VH_Env(init_scene_graph)
    Action_list=['walk_executor(cup_2063)','grab_executor(cup_2063)','walk_executor(clothes_pants_2085)','put_executor(cup_2063,clothes_pants_2085)']

    for action in Action_list:
        if 'put' in str(action):
            print('Action: ',str(action))
        action_crow=CrowControllerApplier(action)
        observation = env.step(action_crow) #Execute action
        
if __name__ == '__main__':
    args = load_config("experiments/virtualhome/VH_scripts/config.yaml")
    evaluate_all(args)
    # evaluate_single(args)
    # check_task_define_all(args)
    # check_task_define_single(args)
    # case_study_easy2hard(args)