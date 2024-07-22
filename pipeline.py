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
from Interpretation import goal_interpretation
from solver import goal_solver

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

def transform_plan(plan):
    # 分隔输入字符串
    executors = plan[0].split(';')
    
    # 定义一个空的列表来存储转换后的动作
    actions = []
    
    # 遍历每个执行器并应用映射规则
    for executor in executors:
        # 提取动作和目标
        action, target = executor.replace(')', '').split('(')
        action = action.replace('_executor', '').upper()
        
        # 生成新的格式并添加到列表中
        actions.append(f'[{action}] <{target}>')
    
    return actions

def run(graph_path,script_path,goal,additional_information):
    #import objects and stats information from graph
    graph = utils.load_graph(graph_path)
    get_nodes_information(graph)
    objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(graph)
    construct_cdl(objects,states,relationships,properties,cat_statement)
    script,brief_discription,introduction = read_script(script_path)

    #goal interpretation
    goal_int=goal_interpretation(goal,additional_information,classes)
    print("Goal interpretation is:\n",goal_int)
    with open("generated.cdl", "r") as file:
        original_content = file.read()
    combined_content = original_content + "\n" + goal_int
    new_file_path = "combined_generated.cdl"
    with open(new_file_path, "w") as file:
        file.write(combined_content)
    
    print(f"Combined content saved to {new_file_path}")
    #planning
    plan=goal_solver(original_content + "\n" + goal_int)
    plan=transform_plan(plan)
    print(plan)
    #execution
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
    goal="turn off all the lights"
    additional_information=None
    # data_path="data/programs_processed_precond_nograb_morepreconds/"
    # with open("combined_generated.cdl", "r") as file:
    #     original_content = file.read()
    # goal_solver(original_content)
    run(graph_path,script_path,goal,additional_information)
    
    
    