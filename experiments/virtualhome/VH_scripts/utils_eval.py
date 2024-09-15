import os
import json
import re
import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main')
from virtualhome_eval.simulation.evolving_graph.environment import EnvironmentGraph, Property
from virtualhome_eval.simulation.evolving_graph.execution import Relation, State
from virtualhome_eval.simulation.evolving_graph.scripts import *


def construct_cdl(objects,states,relationships,properties,cat_statement):
    exploration_content=''
    problem_file_content = 'problem "virtualhome-problem"\n'
    problem_file_content += 'domain "virtualhome.cdl"\n\n'
    problem_file_content += '#!pragma planner_is_goal_serializable=False\n'
    problem_file_content += '#!pragma planner_is_goal_ordered=True\n'
    problem_file_content += '#!pragma planner_always_commit_skeleton=True\n\n'
    problem_file_content += 'objects:\n'
    problem_file_content+='#objects\n\n'
    for obj in objects:
        problem_file_content += f'  {obj}\n'
    problem_file_content+="#object_end\n\n"
    problem_file_content += '\ninit:\n'

    problem_file_content += '#states\n\n'
    for init_state in states:
        if "unknown" in init_state:
            exploration_content+=f'  {init_state}\n'
            continue
        problem_file_content += f'  {init_state}\n'
    problem_file_content += '#states_end\n\n'

    problem_file_content += '#relations\n\n'
    for init_state in relationships:
        if "checked" in init_state:
            exploration_content+=f'  {init_state}\n'
            continue
        problem_file_content += f'  {init_state}\n'
    problem_file_content += '#relations_end\n\n'
    
    problem_file_content += '#properties\n\n'
    for init_state in properties:
        problem_file_content += f'  {init_state}\n'
    problem_file_content += '#properties_end\n\n'
    problem_file_content += '#categories\n\n'
    for cat in cat_statement:
        problem_file_content += f'  {cat}\n'
    problem_file_content += '#categories_end\n\n'
    # Write the content to a file
    problem_file_content += '#exploration\n\n'
    problem_file_content += exploration_content
    problem_file_content += '#exploration_end\n\n'


    problem_file_content += '#id\n\n'


    for obj in objects:
        if '_' in obj:
            id=re.search(r'_(\d+):', obj).group(1)
            name=obj.split(':')[0]
            problem_file_content += f'  id[{name}]={id}\n'
    problem_file_content += '#id_end\n\n'
    
    with open("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/init_scene.cdl", "w") as file:
        file.write(problem_file_content)
    

def extract_script(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        task_name = lines[0]
        task_description = lines[1]
        actions = [line.strip() for line in lines if line.startswith("[")]
    return task_name, task_description, actions

def get_from_dataset(dataset_root, scenegraph_id, script_id):
    dataset_root="/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/dataset/programs_processed_precond_nograb_morepreconds"
    scene_dir = os.path.join(
        dataset_root,
        "init_and_final_graphs",
        f"TrimmedTestScene{scenegraph_id}_graph",
        "results_intentions_march-13-18",
        f"file{script_id}.json",
    )
    graph_dict = json.load(open(scene_dir, "r"))
    init_scene_state = graph_dict["init_graph"]
    init_scene_graph = EnvironmentGraph(init_scene_state)
    final_state_dict = graph_dict["final_graph"]

    script_dir = os.path.join(
        dataset_root,
        "executable_programs",
        f"TrimmedTestScene{scenegraph_id}_graph",
        "results_intentions_march-13-18",
        f"file{script_id}.txt",
    )

    task_name, task_description, actions = extract_script(script_dir)
    return init_scene_graph, actions, final_state_dict, task_name, task_description

def reformat_actions(commands):
    reformatted_commands = []
    relevant_id = []
    for command in commands:
        parts = command.split()
        # Assuming the format is consistent as described: [action] <object> (id) or [action] <object1> (id1) <object2> (id2)
        reformatted_command = parts[0]  # This should be [action_name]
        for part in parts[1:]:
            if "(" in part and ")" in part:
                id_number = part.split(".")[-1]
                id_number = "(" + id_number[:-1] + ")"
                reformatted_command += f" {id_number}"
                id_number = int(id_number.strip("(").strip(")"))
                relevant_id.append(id_number)
            else:
                # This is an object name or a part of it
                reformatted_command += f" {part}"
        reformatted_commands.append(reformatted_command)
    relevant_id = list(set(relevant_id))
    return reformatted_commands, relevant_id


def state_translation(objname, state):
    mapping = {
    "CLOSED": "closed[x: item]",
    "OPEN": "open[x: item]",
    "ON": "is_on[x: item]",
    "OFF": "is_off[x: item]",
    "SITTING": "sitting[x: character]",
    "DIRTY": "dirty[x: item]",
    "CLEAN": "clean[x: item]",
    "LYING": "lying[x: character]",
    "PLUGGED_IN": "plugged[x: item]",
    "PLUGGED_OUT": "unplugged[x: item]",
    "SURFACES": "surfaces[x: item]",
    "GRABBABLE": "grabbable[x: item]",
    "SITTABLE": "sittable[x: item]",
    "LIEABLE": "lieable[x: item]",
    "HANGABLE": "hangable[x: item]",
    "DRINKABLE": "drinkable[x: item]",
    "EATABLE": "eatable[x: item]",
    "RECIPIENT": "recipient[x: item]",
    "CUTTABLE": "cuttable[x: item]",
    "POURABLE": "pourable[x: item]",
    "CAN_OPEN": "can_open[x: item]",
    "HAS_SWITCH": "has_switch[x: item]",
    "READABLE": "readable[x: item]",
    "LOOKABLE": "lookable[x: item]",
    "CONTAINERS": "containers[x: item]",
    "CLOTHES": "is_clothes[x: item]",
    "PERSON": "person[x: item]",
    "BODY_PART": "body_part[x: item]",
    "COVER_OBJECT": "cover_object[x: item]",
    "HAS_PLUG": "has_plug[x: item]",
    "HAS_PAPER": "has_paper[x: item]",
    "MOVABLE": "movable[x: item]",
    "CREAM": "cream[x: item]",
}

    state_name=state.name
    feature = mapping.get(state_name, "Unknown feature")
    result= feature.replace("x: item", f"{objname}").replace("x: character", f"x: {objname}")+" = True".replace("-","_")
    return result

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

def get_nodes_information(graph):
    with open("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/resources/class_name_equivalence.json", "r") as file:
        equal_dict=json.load(file)
    nodes=graph.get_nodes()
    edges=graph.get_edges()
    objects=[]
    category=[]
    states=[]
    relationships=[]
    properties=[]
    classes=[]
    cat_statement=[]
    unknown_set=set()

    for node in nodes:
        executable_objname=(node.class_name).replace("-","_")+'_'+str(node.id)
        if node.category !='Characters':
            category.append(node.category)
            classes.append(node.class_name)
            objects.append(executable_objname+":item")
            op_classname=node.class_name.replace("-","_")
            cat_statement.append(f"is_{op_classname}[{executable_objname}]=True")

            if op_classname in equal_dict:
                for equal_name in equal_dict[op_classname]:
                    if equal_name!=op_classname:
                        cat_statement.append(f"is_{equal_name}[{executable_objname}]=True")
            for equal_name in equal_dict:
                if op_classname in equal_dict[equal_name] and op_classname!=equal_name:
                    cat_statement.append(f"is_{equal_name}[{executable_objname}]=True")
                    for equal_name_ in equal_dict[equal_name]:
                        if equal_name!=op_classname:
                            cat_statement.append(f"is_{equal_name_}[{executable_objname}]=True")


            for property in node.properties:
                property=state_translation(executable_objname,property)
                properties.append(property)
                if "grabbable" in property:
                    states.append(f"unknown[{executable_objname}]=True")
                    unknown_set.add(executable_objname)
                if "food" in executable_objname:
                    properties.append(f"is_food[{executable_objname}]=True")

            for state in node.states:
                if executable_objname in unknown_set:
                    continue
                state=state_translation(executable_objname,state)
                states.append(state)
            

        if node.category=="Rooms":
            states.append(f"is_room[{executable_objname}]=True")
        
    for edge in edges:
        relationship=relationship_translation(graph,edge)
        from_name=graph._node_map[edge['from_id']].class_name+'_'+str(edge['from_id'])
        to_name=graph._node_map[edge['to_id']].class_name+'_'+str(edge['to_id'])
        if from_name in unknown_set or to_name in unknown_set:
            continue
        relationships.append(relationship)

    objects.append("char:character")
            # print(node.class_name,node.states)
    return objects,states,relationships,properties,list(set(category)),list(set(classes)),cat_statement

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

def transform_action(action,scripts_index):
    # 分隔输入字符串
    action=str(action).replace('_executor', '')
    action = action.replace(')', '')
    action = action.replace('(', ' ')
    action = action.split()
    # 提取动作和目标
    action_name = action[0].upper()
    if action_name=='PUT' or action_name=='PUTIN':
        if action_name=='PUT':
            action_name="PUTBACK"
        from_obj=action[1].replace(',','')
        to_obj=action[2]
        from_o=''
        to_o=''
        if '_' in from_obj:
            item, number = from_obj.rsplit('_', 1)
            from_o = f'<{item}>({number})'
        else:
            from_o = from_obj
        if '_' in to_obj:
            item, number = to_obj.rsplit('_', 1)
            to_o = f'<{item}>({number})'
        else:
            to_o = to_obj
        return [parse_script_line(f'[{action_name}] {from_o} {to_o}',scripts_index)]
    else:
        target = action[1]
        if '_' in target:
            item, number = target.rsplit('_', 1)
            formatted_target = f'<{item}>({number})'
        else:
            formatted_target = target
        return [parse_script_line(f'[{action_name}] {formatted_target}',scripts_index)]
    
def check_unexplorable(location_name):
    if location_name=='char':
        return True
    location_category='_'.join(location_name.split('_')[:-1])
    unexplorable_list=['room','wall','ceiling','bathroom','bedroom','dining_room','floor']
    return location_category in unexplorable_list