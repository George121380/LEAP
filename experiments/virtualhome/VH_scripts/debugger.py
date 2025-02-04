# ----------------------------------------------
# Debugger, Task test, Scene test
# ----------------------------------------------


import sys
from tqdm import tqdm
sys.setrecursionlimit(1000000)
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
    for task_file in tqdm(files):
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

    config.scene_id = 0
    # Action_list=['walk_executor(kitchen_counter_230)','walk_executor(stove_2065)','walk_executor(sink_231)','walk_executor(faucet_232)','walk_executor(cupboard_229)','walk_executor(pot_2069)','open_executor(cupboard_229)','grab_executor(pot_2069)','walk_executor(faucet_232)','switchon_executor(faucet_232)','putin_executor(pot_2069, faucet_232)','switchoff_executor(faucet_232)']
    Action_list=[]


    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Cook_some_food/g8_test.txt'


    epoch_path=f'log/Debugging'   
    epoch_logger = setup_epoch_logger(epoch_path)
    evaluator=Evaluator(config,task_path,epoch_logger,epoch_path)
    classes,init_scene_graph=load_scene(config.scene_id, epoch_path)
    env=VH_Env(init_scene_graph)
    evaluator.left_action_counting_for_each_keystate() # Check the task define before executing the actions
    # return
    if len(Action_list)==0:
        return
    for action in Action_list:
        action_crow=CrowControllerApplier(action)
        observation = env.step(action_crow) #Execute action
        evaluator.updates(observation)
    evaluator.left_action_counting_for_each_keystate() # Check the task define after executing the actions

if __name__ == '__main__':

    # check_task_define_all(config)
    check_task_define_single(config)
    # test_action_sequence(2)



    