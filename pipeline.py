import json
import sys
sys.path.append('../simulation')
import evolving_graph.utils as utils
from evolving_graph.execution import Relation, State
from evolving_graph.scripts import *
from evolving_graph.execution import ScriptExecutor
from evolving_graph.environment import EnvironmentGraph
from evolving_graph.preparation import AddMissingScriptObjects, AddRandomObjects, ChangeObjectStates, \
    StatePrepare, AddObject, ChangeState, Destination
from evolving_graph.environment import *
from utils import get_nodes_information,construct_cdl
from additional_information_interpretation import interpretation
from solve_virtualhome import goal_solver

def print_node_names(n_list):
    if len(n_list) > 0:
        print([n.class_name for n in n_list])

def get_node_by_name(name,graph):
    nodes=graph.get_nodes()
    for node in nodes:
        if node.class_name == name:
            return node
    else:
        return None

def run(graph_path,script_path):
    graph = utils.load_graph(graph_path)
    get_nodes_information(graph)
    objects,states,relationships,properties=get_nodes_information(graph)
    construct_cdl(objects,states,relationships,properties)
    script,brief_discription,introduction = read_script(script_path)
    introduction="Prepare for the dinner for two people"
    goal_interpretation=interpretation(introduction,objects)
    print("Goal interpretation is:\n",goal_interpretation)

    goal_solver(goal_interpretation)
    name_equivalence = utils.load_name_equivalence()
    plate = get_node_by_name('cup',graph)
    print(plate.states)   
    
    executor = ScriptExecutor(graph, name_equivalence)
    state_enum = executor.find_solutions(script)
    state = next(state_enum, None)
    
    if state is None:
        print('Script is not executable.')
    else:
        print('Script is executable')
        plate = state.get_nodes_by_attr('class_name', 'plate')
        if len(plate) > 0:
            print("plate states are:", plate[0].states)
        
        chars = state.get_nodes_by_attr('class_name', 'character')
        if len(chars) > 0:
            char = chars[0]
            print("Character holds:")
            print_node_names(state.get_nodes_from(char, Relation.HOLDS_RH))
            print_node_names(state.get_nodes_from(char, Relation.HOLDS_LH))
            print("Character is on:")
            print_node_names(state.get_nodes_from(char, Relation.ON))
            print("Character is in:")
            print_node_names(state.get_nodes_from(char, Relation.INSIDE))
            print("Character states are:", char.states)


if __name__ == '__main__':
    graph_path='test_graph.json'
    script_path='test_script.txt'

    data_path="data/programs_processed_precond_nograb_morepreconds/"
    run(graph_path,script_path)
    