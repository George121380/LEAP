# ----------------------------------------------
# Cooking Tasks
# ----------------------------------------------

import sys
import json
sys.path.append('../cdl_dataset/scripts')
sys.path.append('')
from datetime import datetime
from utils_eval import CrowControllerApplier, load_config, namespace_to_dict
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
from main_VH import run
DATASET_FOLDER_PATH = 'cdl_dataset/cooking'

sys.setrecursionlimit(1000000)

def cooking_task_loader(folder_path, difficulty):
    all_files = []
    subdir_path = os.path.join(folder_path, difficulty)
    files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
    for file in files:
        if not 'bug' in file:
            all_files.append(os.path.join(subdir_path,file))
    return all_files


def evaluate_all_cross_scene(config): # main function
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

        load_library = input("Do you want to load the library (y/n)? ").strip()
        if load_library == 'y':
            library_path = input("Enter the path to the library: ").strip()
            with open(library_path, 'r') as file:
                library = json.load(file)
            with open(f'{epoch_path}/library_data.json', 'w') as file:
                json.dump(library, file, indent=4)

        
        difficulty = input("Please input the difficulty level (easy, middle, hard): ")
        if difficulty not in ['easy', 'middle', 'hard']:
            raise Exception('Invalid difficulty level')
        files = cooking_task_loader(DATASET_FOLDER_PATH, difficulty)
        scenes=[0,1,2]
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
        task_path=task_scene_pair[0]
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

    print("\nDo you want to use checkpoint (y/n)?")
    checkpoint_choice = input("Enter the letter: ").strip()
    if checkpoint_choice == 'y':
        config.checkpoint = input("Enter the path to the checkpoint: ").strip()
    else:
        config.checkpoint = ''
    evaluate_all_cross_scene(config)