# from env_kitchen import Agent,KitchenEnvironment
import sys
import json
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/evaluation/action_sequence/scripts')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')

from experiments.virtualhome.VH_scripts.agent import VHAgent
from utils_eval import get_from_dataset,get_nodes_information,construct_cdl
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time
from logger import logger
from human import Human
random.seed(time.time())

def load_task():
    scene_path='cdl_dataset/Scene.json'
    with open(scene_path) as f:
        scene=json.load(f)
    init_scene_graph = EnvironmentGraph(scene)
    taskset_path='cdl_dataset/discription.json'
    with open(taskset_path) as f:
        taskset=json.load(f)
    taskset=taskset['scene_1']
    id=random.randint(0,len(taskset)-1)
    task=taskset[id]
    goal=task['goals']['g2']
    # goal='Make some potato chicken noodle, put it in a box, and store it in the fridge.'
    additional_information=''
    objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(init_scene_graph)
    construct_cdl(objects,states,relationships,properties,cat_statement)
    return goal,additional_information,classes,init_scene_graph
    

def run(goal,additional_information,classes,init_scene_graph):
    init_path="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/init_scene.cdl"
    agent=VHAgent(init_path)
    agent.set_human_helper(Human(init_scene_graph))
    # agent.human_helper.QA("Can you help me to find basket_for_clothes_2006 ?")
    agent.reset_goal(goal,additional_information,classes,First_time=True)#ini a GR
    env=VH_Env(init_scene_graph)
    while True:
        action,plan = agent.act() #Planning    
        # action=ACTION('walk_executor')
        if action=="over":
            env.report_actions()
            return #Planning failed -> reset goal base on current state
        
        #['Goal Representation', 'Debug Result', 'Action', 'Add Info','Query Human']
        print('Action: ',action)
        observation = env.step(action) #Execute action
        agent.updates(observation) #Update agent's state

def evaluate():
    goal,additional_information,classes,init_scene_graph=load_task()
    logger.info(goal,"","","","","")
    print(goal)
    run(goal,additional_information,classes,init_scene_graph)


if __name__ == '__main__':
    evaluate() # cook a chicken