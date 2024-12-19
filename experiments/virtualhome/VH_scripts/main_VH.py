import sys
import json
import re
sys.path.append('cdl_dataset/scripts')
sys.path.append('')
from datetime import datetime
from experiments.virtualhome.VH_scripts.agent import VHAgent
from experiments.virtualhome.VH_scripts.agent_LLM import LLM_Agent
from utils_eval import get_nodes_information,construct_cdl, CrowControllerApplier, load_config, evaluation_task_loader, namespace_to_dict
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time
from logger import setup_task_logger, setup_epoch_logger, get_last_task_path_from_logger, filter_tasks
from human import Human
from evaluation import Evaluator
random.seed(time.time())
import pdb
import yaml 
import os
from dataset import parse_file_to_json
from tqdm import tqdm
import shutil

INIT_PATH_PO = "experiments/virtualhome/CDLs/init_scene_PO.cdl"
INIT_PATH_NPO = "experiments/virtualhome/CDLs/init_scene_NPO.cdl"
DATASET_FOLDER_PATH = 'cdl_dataset/dataset'
running_mode='test' #debug or test 

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

def task_summary_record(epoch_logger, scene_id, goal, action_history, start_time, complete_rate, task_path, final_info):
    """
    Record the summary of a task execution.
    """
    current_time = time.time()
    time_elapsed = int(current_time - start_time) if start_time else ''
    time_info = f"Time consume: {time_elapsed} seconds\nExp_helper query times: {final_info['exp_helper_query_times']}\nGuidance query times: {final_info['guidance_query_times']}\nlibrary scale: {final_info['library_scale']}"
    epoch_logger.info(task_path, goal, action_history, time_info, complete_rate, f"Scene_id: {str(scene_id)}")
    
def run(args,epoch_logger,epoch_path,task_path,classes,init_scene_graph):
    """
    Execute a single task with the specified agent.
    """
    start_time = time.time()
    log_name = f"{os.path.basename(os.path.dirname(task_path))}_{os.path.basename(task_path).replace('.txt', '')}_scene_{args.scene.id}"
    folder_path = f'{epoch_path}/records'

    # Set the task logger
    task_logger = setup_task_logger(folder_path,task_name=log_name)

    task_data=parse_file_to_json(task_path)
    evaluator=Evaluator(args,task_path,task_logger,epoch_path)

    # Setup agent based on the model type
    if args.model.type=='ours':
        args.agent_type='Planning'
        agent = VHAgent(
            args=args, 
            filepath=INIT_PATH_PO, 
            task_logger=task_logger, 
            PO=True, 
            epoch_path=epoch_path
        )
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],classes,task_data['Task name'],First_time=True)#ini a GR
        agent.download_behaviors_from_library()

    if args.model.type=='LLM':
        agent = LLM_Agent(
            args=args,
            filepath=INIT_PATH_PO,
            task_logger=task_logger,
            epoch_path=epoch_path
        )
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],task_data['Task name'])#ini a GR
        agent.item_infoto_nl()

    if args.model.type=='LLM+P':
        pass

    if args.model.type=='CAP':
        args.agent_type='Policy'
        agent = VHAgent(
            args=args, 
            filepath=INIT_PATH_PO, 
            task_logger=task_logger, 
            PO=True, 
            epoch_path=epoch_path
        )
        agent.set_human_helper(Human(init_scene_graph,task_data['Guidance']))
        agent.reset_goal(task_data['Goal'],classes,task_data['Task name'],First_time=True)#ini a GR
        agent.download_behaviors_from_library()

    ######## Test Human Guidance ########
    # log_path = f'log/epoch_{timestamp}/test_all_human_guidance.json'
    
    # # Ensure the file exists and has valid JSON
    # if os.path.exists(log_path):
    #     with open(log_path, 'r') as f:
    #         try:
    #             existing_data = json.load(f)
    #         except json.JSONDecodeError:
    #             existing_data = []
    # else:
    #     existing_data = []
    
    # Human_Guidance=[]
    # Human_Guidance.append({'task_name':log_name,'goal':task_data['Goal'],'guidance':task_data['Guidance']})
    # for sub_goal in agent.sub_goal_list:
    #     question=re.sub(r'^\d+[\.\:]?\s*', '', sub_goal.lower())
    #     question="Can you tell me how to "+question
    #     print("#"*80)
    #     print(question)
    #     print("#"*80)
    #     answer=agent.query_LLM_human(question)
    #     # Human_Guidance.append(answer)
    #     question_pair={'question':question,'answer':answer}
    #     Human_Guidance.append(question_pair)

    # existing_data.append(Human_Guidance)
    
    # # Save the updated data
    # with open(log_path, 'w') as f:
    #     json.dump(existing_data, f, indent=4)
    ######## Test Human Guidance ########

    env=VH_Env(init_scene_graph)

    while True:
        try:
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
                    task_summary_record(epoch_logger,args.scene.id,task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.final_important_numbers_report())
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
                    agent.lift_behaviors()
                    if epoch_logger:
                        task_summary_record(epoch_logger,args.scene.id,task_data['Goal'],executed_actions,start_time,1,task_path,agent.final_important_numbers_report())
                    return True
                else:
                    if epoch_logger:
                        task_summary_record(epoch_logger,args.scene.id,task_data['Goal'],executed_actions,start_time,complete_rate,task_path,agent.final_important_numbers_report())
                return True
            
            print('Action: ',str(action))
            observation = env.step(action) #Execute action
            agent.updates(observation) #Update agent's state
            evaluator.updates(observation) #Update evaluator's state
            if not 'obs' in action.name and not 'exp' in action.name:
                evaluation_result=evaluator.evaluate(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
                
        except Exception as e:
            print(e)
            evaluation_result,complete_rate=evaluator.evaluate_final(ast=None,action_history=agent.add_info_action_history_for_evaluation,Root=True)
            executed_actions=env.report_actions()
            task_summary_record(epoch_logger,args.scene.id,'Syntax Error',executed_actions,start_time,complete_rate,task_path,agent.final_important_numbers_report())
            return False
       
def evaluate_single(args):
    start_time = time.time()
    # print('Start Time: ',start_time)
    args.scene.id = 2
    classes,init_scene_graph=load_scene(args.scene.id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}')
    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Prepare_breakfast/g4.txt'
    run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph)
    # test_simulator(init_scene_graph)
    end_time = time.time()
    # print('End Time: ',end_time)
    print('Time Consumed: ',end_time-start_time)

def evaluate_all(args): # main function
    files=evaluation_task_loader(DATASET_FOLDER_PATH)
    random.shuffle(files)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Set logger and save configs
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    with open(f'log/epoch_{timestamp}/args.yaml', 'w') as file:
        yaml.dump(namespace_to_dict(args), file)
    
    files = tqdm(files, desc="Evaluating tasks")

    for task_file in files:
        classes,init_scene_graph=load_scene(args.scene.id)
        task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
        Debug=run(args,epoch_logger,timestamp,task_path,classes,init_scene_graph)
        if Debug==False:
            raise Exception('Error in evaluation')
    end_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger.info('Evaluation Finished',end_time,'','','','')

def evaluate_all_cross_scene(args): # main function

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.isdir(args.checkpoint.log_dir) and args.checkpoint.log_dir != '':
        print('Continue training base on the checkpoint')
        input("Press Enter to continue...")
        epoch_path = f'{args.checkpoint.log_dir}_continue'
        shutil.copytree(args.checkpoint.log_dir, epoch_path)
        print(f"The continue folder is create at: {epoch_path}")
        with open(f'{epoch_path}/shuffled_task_scene_pairs.json', 'r') as file:
            task_scene_pairs = json.load(file)
        epoch_logger = setup_epoch_logger(epoch_path)
        csv_handler = epoch_logger.handlers[0]
        last_task_path, last_task_scene_num = get_last_task_path_from_logger(csv_handler)
        print()
        print("Lastest Task Path:", last_task_path)
        task_scene_pairs=filter_tasks(task_scene_pairs, last_task_path, last_task_scene_num)

    
    else:
        # Create a new folder for the epoch
        epoch_path = f'log/epoch_{timestamp}'
        epoch_logger = setup_epoch_logger(epoch_path)

        if running_mode == 'test':
            with open('experiments/virtualhome/VH_scripts/shuffled_task_scene_pairs.json', 'r') as file:
                task_scene_pairs = json.load(file)
        else:
            files=evaluation_task_loader(DATASET_FOLDER_PATH)
            scenes=[0,1,2]
            # Use a random order for the tasks
            task_scene_pairs = [(task, scene) for task in files for scene in scenes]
            random.shuffle(task_scene_pairs)
        with open(f'{epoch_path}/args.yaml', 'w') as file:
            yaml.dump(namespace_to_dict(args), file)
        with open(f'{epoch_path}/shuffled_task_scene_pairs.json', 'w') as file:
            json.dump(task_scene_pairs, file, indent=4)
        
    
    task_scene_pairs = tqdm(task_scene_pairs, desc="Evaluating tasks")

    for task_scene_pair in task_scene_pairs:
        args.scene.id = task_scene_pair[1]
        classes,init_scene_graph=load_scene(args.scene.id)
        task_path=os.path.join(DATASET_FOLDER_PATH,task_scene_pair[0])
        Debug=run(args,epoch_logger,epoch_path,task_path,classes,init_scene_graph)
        
        # if Debug==False:
        #     raise Exception('Error in evaluation')
        
    end_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger.info('Evaluation Finished',end_time,'','','','')

def check_task_define_all(args):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    files=evaluation_task_loader(DATASET_FOLDER_PATH)
    random.shuffle(files)
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}',timestamp=timestamp)
    for task_file in files:
        task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
        print(task_path)
        evaluator=Evaluator(args,task_path,epoch_logger,epoch_path)
        evaluator.left_action_counting_for_each_keystate()

def check_task_define_single(args):

    args.scene.id = 0

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}')
   
    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Prepare_breakfast/g4.txt'
    evaluator=Evaluator(args,task_path,epoch_logger,epoch_path)
    # for action in action_list:
    #     evaluator.updates(action)
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
    Action_list=['walk_executor(window_2109)','open_executor(window_2109)']

    for action in Action_list:
        if 'put' in str(action):
            print('Action: ',str(action))
        action_crow=CrowControllerApplier(action)
        observation = env.step(action_crow) #Execute action
        
if __name__ == '__main__':
    args = load_config("experiments/virtualhome/VH_scripts/config.yaml")
    # evaluate_all_cross_scene(args)
    evaluate_single(args)
    # evaluate_all(args)
    # check_task_define_all(args)
    # check_task_define_single(args)
    # case_study_easy2hard(args)