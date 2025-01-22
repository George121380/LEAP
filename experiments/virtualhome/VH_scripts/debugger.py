# ----------------------------------------------
# Debugger, Task test, Scene test
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
import os
from dataset import parse_file_to_json
from tqdm import tqdm
from configs import OursWG, OursWOG, LLMWG, LLMWOG, LLMPlusPWG, LLMPlusPWOG, CAPWG, CAPWOG, load_scene, set_agent


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

config.checkpoint = ''

DATASET_FOLDER_PATH = 'cdl_dataset/dataset'
running_mode='test' #debug or test 


#################################################
#######          Debugger           #######
#################################################



def check_task_define_all(config):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    files=evaluation_task_loader(DATASET_FOLDER_PATH)
    random.shuffle(files)
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}')
    for task_file in files:
        for scene_id in range(3):
            print('#'*60)
            print('Scene ID: ',scene_id)
            print('Task: ',task_file)
            print('#'*60)
            config.scene_id = scene_id
            task_path=os.path.join(DATASET_FOLDER_PATH,task_file)
            print(task_path)
            evaluator=Evaluator(config,task_path,epoch_logger,epoch_path)
            evaluator.left_action_counting_for_each_keystate()

def check_task_define_single(config):

    config.scene_id = 1

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epoch_path=f'log/epoch_{timestamp}'
    epoch_logger = setup_epoch_logger(f'log/epoch_{timestamp}')
   
    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Drink/g5.txt'
    evaluator=Evaluator(config,task_path,epoch_logger,epoch_path)
    # for action in action_list:
    #     evaluator.updates(action)
    evaluator.left_action_counting_for_each_keystate()

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
    # evaluate_all_cross_scene(config)
    # evaluate_single(config)
    # evaluate_all(config)
    check_task_define_all(config)
    # check_task_define_single(config)
    # case_study_easy2hard(config)