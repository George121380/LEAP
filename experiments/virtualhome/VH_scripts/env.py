import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
from execution import ScriptExecutor
from utils import load_name_equivalence
from utils_eval import transform_action
from scripts import *



class VH_Env:
    def __init__(self, graph):
        name_equivalence = load_name_equivalence()
        self.executor = ScriptExecutor(graph, name_equivalence)

    def step(self, action):
        action=transform_action(action)
        script=Script(action)
        state_enum = self.executor.find_solutions(script)
        state = next(state_enum, None)
        if state is None:
            print('Script is not executable.')
        else:
            print('Script is executable')
