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

def relationships_with_node(node,graph):
    graph_dict=graph.to_dict()
    id=node.id
    relationships=[]
    for edge in graph_dict['edges']:
        if edge['from_id']==id:
            relationships.append(edge)
    return relationships

def relationships_discription(relationships,graph):
    for relationship in relationships:
        print(relationship['relation_type'],graph.get_node_map()[relationship['to_id']])


def run():
    graph = utils.load_graph('test_graph.json')
    # print("plate states are:", ini_plate.states)
    name_equivalence = utils.load_name_equivalence()
    plate = get_node_by_name('cup',graph)
    relationships=relationships_with_node(plate,graph)
    print(plate.states)   
    relationships_discription(relationships,graph)
    # script = read_script('example_scripts/example_script_1.txt')
    script = read_script('test_script.txt')
    executor = ScriptExecutor(graph, name_equivalence)
    state_enum = executor.find_solutions(script)
    state = next(state_enum, None)
    # # Add missing objects (random)
    # properties_data = utils.load_properties_data()
    # object_placing = utils.load_object_placing()
    # prepare_1 = AddMissingScriptObjects(name_equivalence, properties_data, object_placing)

    # # Add 10 random objects
    # prepare_2 = AddRandomObjects(properties_data, object_placing, choices=10)
    # prepare_3 = ChangeObjectStates(properties_data)
    # state_enum = executor.find_solutions(script, [prepare_1, prepare_2, prepare_3])
    # state = next(state_enum, None)
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
    run()
    