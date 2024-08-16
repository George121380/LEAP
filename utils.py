
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
import tqdm
import random
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Agent evaluation")
    parser.add_argument(
        "--mode",
        type=str,
        default="generate_prompts",
        help="generate_prompts, evaluate_results",
    )
    parser.add_argument(
        "--eval_type",
        type=str,
        default="action_sequence",
        help="action_sequence, transition_model, goal_interpretation, subgoal_decomposition",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt-4o-2024-05-13",
        help="model name will be used as directory name to store results: gemini-1.5-pro-preview-0409, gpt-4o-2024-05-13, llama-3-70b-chat, mistral-large-2402,mixtral-8x22b-instruct-v0.1, gpt-4-turbo-2024-04-09, gpt-3.5-turbo-0125,llama-3-8b-chat, claude-3-haiku-20240307, claude-3-opus-20240229,claude-3-sonnet-2024022, cohere-command-r, cohere-command-r-plus, gemini-1.0-pro, gemini-1.5-flash-preview-0514",
    )
    parser.add_argument(
        "--resource_dir",
        type=str,
        default="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/resources",
        help="resources directory",
    )
    parser.add_argument(
        "--llm_response_path", type=str, default="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/llm_response/action_sequencing/gpt-4o-2024-05-13_outputs.json", help="your llm response path"
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset",
        help="dataset directory, necessary only when generating prompts",
    )
    parser.add_argument(
        "--dataset", type=str, default="virtualhome", help="virtualhome, behavior"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/test",
        help="output directory",
    )
    parser.add_argument(
        "--partial_observation",type=bool,default=True,help="whether to use partial observation"
    )
    # virtualhoome
    parser.add_argument("--scene_id", type=int, default=1, help="virtualhome scene id")
    return parser.parse_args()

def state_translation(objname, state):
    mapping = {
    State.CLOSED: "closed[x: item]",
    State.OPEN: "open[x: item]",
    State.ON: "is_on[x: item]",
    State.OFF: "is_off[x: item]",
    State.SITTING: "sitting[x: character]",
    State.DIRTY: "dirty[x: item]",
    State.CLEAN: "clean[x: item]",
    State.LYING: "lying[x: character]",
    State.PLUGGED_IN: "plugged[x: item]",
    State.PLUGGED_OUT: "unplugged[x: item]",
    Property.SURFACES: "surfaces[x: item]",
    Property.GRABBABLE: "grabbable[x: item]",
    Property.SITTABLE: "sittable[x: item]",
    Property.LIEABLE: "lieable[x: item]",
    Property.HANGABLE: "hangable[x: item]",
    Property.DRINKABLE: "drinkable[x: item]",
    Property.EATABLE: "eatable[x: item]",
    Property.RECIPIENT: "recipient[x: item]",
    Property.CUTTABLE: "cuttable[x: item]",
    Property.POURABLE: "pourable[x: item]",
    Property.CAN_OPEN: "can_open[x: item]",
    Property.HAS_SWITCH: "has_switch[x: item]",
    Property.READABLE: "readable[x: item]",
    Property.LOOKABLE: "lookable[x: item]",
    Property.CONTAINERS: "containers[x: item]",
    Property.CLOTHES: "clothes[x: item]",
    Property.PERSON: "person[x: item]",
    Property.BODY_PART: "body_part[x: item]",
    Property.COVER_OBJECT: "cover_object[x: item]",
    Property.HAS_PLUG: "has_plug[x: item]",
    Property.HAS_PAPER: "has_paper[x: item]",
    Property.MOVABLE: "movable[x: item]",
    Property.CREAM: "cream[x: item]",
}

    feature = mapping.get(state, "Unknown feature")
    return feature.replace("x: item", f"{objname}").replace("x: character", f"x: {objname}")+" = True".replace("-","_")

def relationship_translation(graph,edge):
    relation_mapping = {
        "ON": "on",
        "INSIDE": "inside",
        "BETWEEN": "between",
        "CLOSE": "close",
        "FACING": "facing",
        "HOLDS_RH": "holds_rh",
        "HOLDS_LH": "holds_lh"
    }
    relation_type=edge['relation_type']
    # if relation_type=="BETWEEN":
    #     print("between relation")
    if graph._node_map[edge['from_id']].class_name=="character":
        from_obj_name="char"
    
    else:
        from_obj_name=graph._node_map[edge['from_id']].class_name+'_'+str(edge['from_id'])
    if graph._node_map[edge['to_id']].class_name=="character":
        to_obj_name="char"
    else:
        to_obj_name=graph._node_map[edge['to_id']].class_name+'_'+str(edge['to_id'])
    if relation_type in relation_mapping:
        relation = relation_mapping[relation_type]
        if graph._node_map[edge['from_id']].class_name=="character":
            if relation=="on":
                relation="on_char"
            if relation=="inside":
                relation="inside_char"
            if relation=="facing":
                relation="facing_char"
            if relation=="close":
                relation="close_char"

        return f"{relation}[{from_obj_name},{to_obj_name}]=True".replace("-","_")
    else:
        relation = "Unknown relation"

def construct_cdl(objects,states,relationships,properties,cat_statement):
    problem_file_content = 'problem "virtualhome-problem"\n'
    problem_file_content += 'domain "virtualhome.cdl"\n\n'
    problem_file_content += '#!pragma planner_is_goal_serializable=False\n'
    problem_file_content += '#!pragma planner_is_goal_ordered=True\n'
    problem_file_content += '#!pragma planner_always_commit_skeleton=True\n\n'
    problem_file_content += 'objects:\n'
    for obj in objects:
        problem_file_content += f'  {obj}\n'
    problem_file_content += '\ninit:\n'
    for init_state in states:
        problem_file_content += f'  {init_state}\n'
    for init_state in relationships:
        problem_file_content += f'  {init_state}\n'
    for init_state in properties:
        problem_file_content += f'  {init_state}\n'
    for cat in cat_statement:
        problem_file_content += f'  {cat}\n'
    
    # Write the content to a file
    with open("generated.cdl", "w") as file:
        file.write(problem_file_content)

def get_nodes_information(graph):
    nodes=graph.get_nodes()
    edges=graph.get_edges()
    objects=[]
    category=[]
    states=[]
    relationships=[]
    properties=[]
    classes=[]
    cat_statement=[]
    for node in nodes:
        executable_objname=(node.class_name).replace("-","_")+'_'+str(node.id)
        if node.category !='Characters':
            category.append(node.category)
            classes.append(node.class_name)
            objects.append(executable_objname+":item")
            op_classname=node.class_name.replace("-","_")
            cat_statement.append(f"is_{op_classname}[{executable_objname}]=True")
            for state in node.states:
                state=state_translation(executable_objname,state)
                states.append(state)
            for property in node.properties:
                property=state_translation(executable_objname,property)
                properties.append(property)

        if node.category=="Rooms":
            states.append(f"is_room[{executable_objname}]=True")
        
    for edge in edges:
        relationship=relationship_translation(graph,edge)
        relationships.append(relationship)

    objects.append("char:character")
            # print(node.class_name,node.states)
    return objects,states,relationships,properties,list(set(category)),list(set(classes)),cat_statement

def get_all_files(folder,k):
    file_paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > k:
                        file_paths.append(file_path)
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")
    return file_paths

def get_symmetric_path(file_path, folder1, folder2):
    relative_path = os.path.relpath(file_path, folder1).replace(".txt",".json")
    symmetric_path = os.path.join(folder2, relative_path)
    return symmetric_path

def sampler(folder1, folder2,low_bound=0):
    files_folder1 = get_all_files(folder1,low_bound)
    
    if not files_folder1:
        raise Exception("No files found in the first folder")
    random.seed(time.time())
    random_file = random.choice(files_folder1)
    symmetric_file = get_symmetric_path(random_file, folder1, folder2)
    
    if not os.path.exists(symmetric_file):
        raise Exception(f"Symmetric file not found for {random_file}")
    
    return random_file, symmetric_file


#############################debug#############################



import json

def extract_categories(json_file_path, output_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    category_strings = []
    for item, categories in data.items():
        category_string = f"is_{item}(x:item)"
        category_strings.append(category_string)
    
    with open(output_file_path, 'w') as file:
        for category_string in category_strings:
            file.write(category_string + '\n')

def process_json_file(file_path,catset):
    graph = utils.load_graph(file_path)
    nodes=graph.get_nodes()
    subset=[]
    for node in nodes:
        if node.category !='Characters':
            subset.append(node.class_name)
    
    catset.update(subset)
    return catset



def process_directory(directory):
    catset=set()
    count=0
    for root, dirs, files in tqdm.tqdm(os.walk(directory)):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                catset=process_json_file(file_path,catset)
                count+=1
                if count%10==0:
                    print(len(catset))
    with open("categories.txt", "w") as file:
        for cat in catset:
            file.write(f"is_{cat}(x:item)\n")

def add_feature_to_lines(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:

        lines = infile.readlines()

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in lines:
            modified_line = line.replace("-", "_")
            outfile.write(f"feature {modified_line}")
            

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
        if action=="PUT":
            action="PUTBACK"
            objects=target.split(", ")
            from_obj=objects[0]
            to_obj=objects[1]
            from_o=''
            to_o=''
            if '_' in from_obj:
                item, number = from_obj.rsplit('_', 1)
                
                if item not in item_count:
                    item_count[item] = 0
                if (item in item_count) and number not in id_map:
                    item_count[item] += 1
                
                if number not in id_map:
                    id_map[number] = item_count[item]
                from_o = f'<{item}>({number}.{id_map[number]})'
            else:
                from_o = from_obj
            if '_' in to_obj:
                item, number = to_obj.rsplit('_', 1)
                
                if item not in item_count:
                    item_count[item] = 0
                if (item in item_count) and number not in id_map:
                    item_count[item] += 1
                
                if number not in id_map:
                    id_map[number] = item_count[item]
                to_o = f'<{item}>({number}.{id_map[number]})'
            else:
                to_o = to_obj
            actions.append(parse_script_line(f'[{action}] {from_o} {to_o}',index))
        # 提取目标和编号
        else:
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
            
                
            formatted_target = f'<{item}>({number}.{id_map[number]})'
            # 生成新的格式并添加到列表中
            actions.append(parse_script_line(f'[{action}] {formatted_target}',index))
        index+=1
    
    return actions


# 使用示例
# json_file_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/resources/properties_data.json'
# output_file_path = 'output.txt'
# extract_categories(json_file_path, output_file_path)

# print(f"Categories have been written to {output_file_path}")
                
if __name__ == "__main__":
    # directory_to_process = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/data/programs_processed_precond_nograb_morepreconds/init_and_final_graphs'  # 修改为你的目录路径
    # process_directory(directory_to_process)

    input_file='categories.txt'
    output_file='categories.txt'
    add_feature_to_lines(input_file, output_file)