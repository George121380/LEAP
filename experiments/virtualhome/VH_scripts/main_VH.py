# from env_kitchen import Agent,KitchenEnvironment
import sys
import json

sys.path.append('embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
sys.path.append('cdl_dataset/scripts')

from experiments.virtualhome.VH_scripts.agent import VHAgent
from utils_eval import get_from_dataset,get_nodes_information,construct_cdl
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time
from logger import logger
from human import Human
from evaluation import Evaluator
random.seed(time.time())
import pdb
import os
from dataset import parse_file_to_json

init_path="experiments/virtualhome/CDLs/init_scene_PO.cdl"

def select_random_file(dataset_path):
    subdirs = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
    selected_subdir = random.choice(subdirs)
    subdir_path = os.path.join(dataset_path, selected_subdir)
    files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
    selected_file = random.choice(files)
    return os.path.join(subdir_path, selected_file)

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

    
def run(additional_information,classes,init_scene_graph,guidance):
    task_path=select_random_file('cdl_dataset/dataset')
    # task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Clean_the_bathroom/g2.txt'
    task_data=parse_file_to_json(task_path)
    print('='*60)
    print("Task Path is: ",task_path)
    print("Task Goal is: ",task_data['Goal'])
    print('='*60)
    agent=VHAgent(init_path)
    agent.set_human_helper(Human(init_scene_graph,guidance))
    evaluator=Evaluator(task_path)
    # question='Can you tell how to open the window?'
    # print("Question: ",question)
    # agent.query_human(question)
    # question='Can you tell how to wash clothes by washing machine?'
    # print("Question: ",question)
    # agent.query_human(question)
    # return
    # agent.human_helper.QA("Can you help me to find basket_for_clothes_2006 ?")
    agent.reset_goal(task_data['Goal'],additional_information,classes,task_data['Task name'],First_time=True)#ini a GR
    env=VH_Env(init_scene_graph)
    while True:
        # evaluator.evaluate(ast=None,action_history=agent.add_info_action_history,Root=True)
        action,plan = agent.act() #Planning    
        # action=ACTION('walk_executor')
        if action=="over":
            print("Task Path is: ",task_path)
            print("Task Goal is: ",task_data['Goal'])
            env.report_actions()
            return #Planning failed -> reset goal base on current state
        if action=="human guided":
            continue
        if action=="Failed":
            print("Task Path is: ",task_path)
            print("Task Goal is: ",task_data['Goal'])
            env.report_actions()
            evaluator.evaluate(ast=None,action_history=agent.add_info_action_history,Root=True)
            print("Task failed")
            return
        print('Action: ',action)
        observation = env.step(action) #Execute action
        agent.updates(observation) #Update agent's state
        evaluator.updates(observation) #Update evaluator's state
        evaluator.evaluate(ast=None,action_history=agent.add_info_action_history,Root=True)

def evaluate():
    additional_information,classes,init_scene_graph,guidance=load_scene()
    run(additional_information,classes,init_scene_graph,guidance)


if __name__ == '__main__':
    evaluate()