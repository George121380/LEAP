# ----------------------------------------------
# Main 
# ----------------------------------------------


import sys
import json
sys.path.append('cdl_dataset/scripts')
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
DATASET_FOLDER_PATH = 'cdl_dataset/dataset'

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
    print_task_info(task_data, config.scene_id)

    # # # ----------------- Print Task Info -----------------
    # if config.scene_id==0:
    #     with open('task_info_record.txt','a') as f:
    #         f.write(task_path+'\n')
    #         # f.write(task_data['Goal']+'\n')
    #         f.write('\n')
    # return
    # # # ----------------- Print Task Info -----------------

    evaluator=Evaluator(config, task_path, task_logger, epoch_path)

    agent = set_agent(config, init_scene_graph, task_data, classes, task_logger, epoch_path)

    # agent.ask_for_human_task_guidance()
    # return True
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
    # input the scene id and the task path you want to evaluate
    print("Please input the scene id you want to evaluate, Four Options: 0,1,2")
    scene_id=input()
    config.scene_id = scene_id

    print("Please input the task path you want to evaluate")
    task_path=input()
    # check existance of the task path
    if not os.path.exists(task_path):
        raise Exception('Task path does not exist')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_path = f'log/{timestamp}_{config.logger_name}'
    epoch_logger = setup_epoch_logger(f'log/{timestamp}_{config.logger_name}')

    classes,init_scene_graph=load_scene(config.scene_id, epoch_path)

    run(config,epoch_logger,epoch_path,task_path,classes,init_scene_graph)
    
    end_time = time.time()
    print('Time Consumed: ',end_time-start_time)


def evaluate_all_cross_scene(config): # main function

    # choose the running mode
    print("Please input the running mode, Four Options: debug, test")
    running_mode=input()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if os.path.isdir(config.checkpoint) and config.checkpoint != '':
        print('Continue training base on the checkpoint')
        input("Press Enter to continue...")
        epoch_path = f'{config.checkpoint}_continue'
        shutil.copytree(config.checkpoint, epoch_path)
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
        epoch_path = f'log/{timestamp}_{config.logger_name}'
        epoch_logger = setup_epoch_logger(epoch_path)

        if running_mode == 'test':
            # use a uniform order in test mode
            with open('experiments/virtualhome/VH_scripts/shuffled_task_scene_pairs.json', 'r') as file:
                task_scene_pairs = json.load(file)
        else:
            # you can diy the task_scene_pairs
            files=evaluation_task_loader(DATASET_FOLDER_PATH)
            scenes=[]

            # input the scene id you want to evaluate, Four Options: 0,1,2,all
            print("Please input the scene id you want to evaluate, Four Options: 0,1,2,all")
            input_content=input()

            if input_content.lower()=='all':
                scenes=[0,1,2]
            else:
                scenes.append(int(input_content))
                
            # Use a random order for the tasks
            task_scene_pairs = [(task, scene) for task in files for scene in scenes]
            random.shuffle(task_scene_pairs)

        with open(f'{epoch_path}/config.yaml', 'w') as file:
            yaml.dump(namespace_to_dict(config), file)
        with open(f'{epoch_path}/shuffled_task_scene_pairs.json', 'w') as file:
            json.dump(task_scene_pairs, file, indent=4)
        
    
    task_scene_pairs = tqdm(task_scene_pairs, desc="Evaluating tasks")

    for task_scene_pair in task_scene_pairs:
        config.scene_id = task_scene_pair[1]
        classes,init_scene_graph=load_scene(config.scene_id, epoch_path)
        task_path=os.path.join(DATASET_FOLDER_PATH,task_scene_pair[0])
        Debug=run(config,epoch_logger,epoch_path,task_path,classes,init_scene_graph)
        
        # if Debug==False:
        #     raise Exception('Error in evaluation')
        
    end_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_logger.info('Evaluation Finished',end_time,'','','','')

if __name__ == '__main__':
    """
    Main function: Prompt user to select a config, then select whether to evaluate a single task or all tasks.
    """
    print("Please select the config to use:")
    print("---------- Baselines ----------")
    print("1) OursWG")
    print("2) OursWOG")
    print("3) LLMWG")
    print("4) LLMWOG")
    print("5) LLMPlusPWG")
    print("6) LLMPlusPWOG")
    print("7) CAPWG")
    print("8) CAPWOG")
    print("---------- Ablations ----------")
    print("9) WOLibrary")
    print("10) ActionLibrary")
    print("11) WORefinement")
    print("12) WOSplit")
    print("13) PvP")
    config_choice = input("Enter the number: ").strip()

    if config_choice == '1':
        config = OursWG()
    elif config_choice == '2':
        config = OursWOG()
    elif config_choice == '3':
        config = LLMWG()
    elif config_choice == '4':
        config = LLMWOG()
    elif config_choice == '5':
        config = LLMPlusPWG()
    elif config_choice == '6':
        config = LLMPlusPWOG()
    elif config_choice == '7':
        config = CAPWG()
    elif config_choice == '8':
        config = CAPWOG()
    elif config_choice == '9':
        config = WOLibrary()
    elif config_choice == '10':
        config = ActionLibrary()
    elif config_choice == '11':
        config = WORefinement()
    elif config_choice == '12':
        config = WOSplit()
    elif config_choice == '13':
        config = PvP()
    else:
        raise Exception('Invalid config choice')

    print("\nPlease select the mode:")
    print("1) single (evaluate a single task)")
    print("2) all    (evaluate multiple tasks)")
    mode_choice = input("Enter the number: ").strip()

    

    if mode_choice == '1':
        evaluate_single(config)
    else:
        print("\nDo you want to use checkpoint (y/n)?")
        checkpoint_choice = input("Enter the letter: ").strip()
        if checkpoint_choice == 'y':
            config.checkpoint = input("Enter the path to the checkpoint: ").strip()
        else:
            config.checkpoint = ''
        evaluate_all_cross_scene(config)


        #cdl_dataset/dataset/Wash_windows/g1.txt
        
        #/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Put_groceries_in_Fridge/g1.txt