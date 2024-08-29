# from env_kitchen import Agent,KitchenEnvironment
import sys
import json
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/evaluation/action_sequence/scripts')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
from experiments.virtualhome.VH_scripts.agent import VHAgent
from utils_eval import get_from_dataset,get_nodes_information,construct_cdl
from env import VH_Env

def load_scene(scene_idx,scenegraph=1):

    dataset_root="./embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"
    

    file_id=scene_idx
    init_scene_graph, actions, final_state_dict, task_name, task_description = (get_from_dataset(dataset_root, scenegraph, file_id))
    objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(init_scene_graph)
    construct_cdl(objects,states,relationships,properties,cat_statement)
    return task_name,task_description,classes,init_scene_graph

def run(goal,additional_information,classes,init_scene_graph):
    init_path="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/init_scene.cdl"
    agent=VHAgent(init_path)
    agent.reset_goal(goal,additional_information,classes,First_time=True)#ini a GR
    # env=VirtualhomeEnvironment(init_path)
    env=VH_Env(init_scene_graph)

    while True:
        action,plan = agent.act() #Planning    
        # action=ACTION('walk_executor')
        if action is None:
            agent.reset_goal(goal,additional_information,classes,First_time=True)
            continue #Planning failed -> reset goal base on current state
        print('Action:', action)
        observation = env.step(action) #Execute action
        agent.updates(observation) #Update agent's state

def evaluate(scene_id,scenegraph):
    goal,additional_information,classes,init_scene_graph=load_scene(scene_id,scenegraph)
    print(goal,additional_information)
    run(goal,additional_information,classes,init_scene_graph)


if __name__ == '__main__':
    # evaluate("755_2",1) # cook pasta
    # evaluate("961_1",1) # wash dishes by hand

    # evaluate("101_1",2) # cook a chicken (with more information)
    # evaluate("772_1",1) # cook a chicken
    evaluate("417_1",1) # cook a chicken