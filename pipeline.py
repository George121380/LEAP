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
from utils import get_nodes_information,construct_cdl,sampler
from Interpretation import goal_interpretation,refiner
from solver import goal_solver
from concepts.dm.crow.parsers.cdl_parser import TransformationError
from auto_debugger import auto_debug
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
    executors = plan[0].split('; ')
    
    # 定义一个空的列表来存储转换后的动作
    actions = []
    item_count = {}
    id_map = {}
    # 遍历每个执行器并应用映射规则
    index=1
    for executor in executors:
        # 提取动作和目标
        action, target = executor.replace(')', '').split('(')
        action = action.replace('_executor', '').upper()

        # 提取目标和编号
        if '_' in target:
            item, number = target.rsplit('_', 1)
            
            if item not in item_count:
                item_count[item] = 0
            if (item in item_count) and number not in id_map:
                item_count[item] += 1
            
            if number not in id_map:
                id_map[number] = item_count[item]
        else:
            formatted_target = target
        if action=="PUT":
            action="PUTBACK"
        formatted_target = f'<{item}>({number}.{id_map[number]})'
        # 生成新的格式并添加到列表中
        actions.append(parse_script_line(f'[{action}] {formatted_target}',index))
        index+=1
    
    return actions

def run(graph_path,script_path,goal,additional_information,debug=False):
    #import objects and stats information from graph
    graph = utils.load_graph(graph_path)
    get_nodes_information(graph)
    objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(graph)
    construct_cdl(objects,states,relationships,properties,cat_statement)
    GTscript,brief_discription,introduction = read_script(script_path)

    #goal interpretation
    if debug:
        introduction=goal
    goal_int=goal_interpretation(introduction,additional_information,classes)
    goal_int=refiner(goal_int,additional_information,classes,goal_int)
    with open("generated.cdl", "r") as file:
        original_content = file.read()
    combined_content = original_content + "\n" + goal_int
    new_file_path = "combined_generated.cdl"
    with open(new_file_path, "w") as file:
        file.write(combined_content)
    
    print(f"Combined content saved to {new_file_path}")
    #planning
    planning_try_count = 0
    while planning_try_count < 5:
        try:
            plan=goal_solver(original_content + "\n" + goal_int)
            break
        except TransformationError as e:
            error_info=e.errors
            print("Error information: ",error_info)
            goal_int=auto_debug(error_info,original_content,goal_int,introduction,additional_information,classes)
            combined_content = original_content + "\n" + goal_int
            new_file_path = "combined_generated.cdl"
            with open(new_file_path, "w") as file:
                file.write(combined_content)

        
    if len(plan)==0:
        print('No plan found or the goal is already satisfied.')
        return
    plan=transform_plan(plan)
    print(plan)

    script=Script(plan)
    #execution
    name_equivalence = utils.load_name_equivalence()
    executor = ScriptExecutor(graph, name_equivalence)
    state_enum = executor.find_solutions(script)
    state = next(state_enum, None)
    
    if state is None:
        print('Script is not executable.')
    else:
        print('Script is executable')
        dishwasher = state.get_node(81).states
        if len(dishwasher) > 0:
            print("dishwasher states are:", dishwasher)
        
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


def evaluate():
    script="data/programs_processed_precond_nograb_morepreconds/executable_programs"
    graph="data/programs_processed_precond_nograb_morepreconds/init_and_final_graphs"
    pair=sampler(script,graph,40)
    graph=pair[1]
    print(graph)
    script=pair[0]
    print(script)
    run(graph,script,None,None)

def test(script,graph,additional_information):
    run(graph,script,None,additional_information)

if __name__ == '__main__':
    evaluate()
    # graph_path='test_graph.json'
    # script_path='test_script.txt'
    # goal="turn off all the lights"
    # additional_information=None
    # run(graph_path,script_path,goal,additional_information,debug=True)
    
    script="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/candidates/split10_3.txt"
    graph="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/candidates/split10_3.json"
    additional_information=None
    test(script,graph,additional_information)
    