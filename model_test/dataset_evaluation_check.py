# from env_kitchen import Agent,KitchenEnvironment
import sys
import json

sys.path.append('embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
sys.path.append('experiments/virtualhome/VH_scripts')
sys.path.append('cdl_dataset/scripts')

import random
import time
from evaluation import Evaluator
random.seed(time.time())

init_path="experiments/virtualhome/CDLs/init_scene_PO.cdl"

task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Cook_some_food/g3.txt'
    

def evaluate():
    evaluator=Evaluator(task_path)
    evaluation_result=evaluator.evaluate(ast=None,action_history=['switchon_executor(faucet_43)'],Root=True)

if __name__ == '__main__':
    evaluate()