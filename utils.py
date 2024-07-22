
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
        "CLOSE": "close_item",
        "FACING": "facing_item",
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
    to_obj_name=graph._node_map[edge['to_id']].class_name+'_'+str(edge['to_id'])
    if relation_type in relation_mapping:
        relation = relation_mapping[relation_type]
        if graph._node_map[edge['from_id']].class_name=="character":
            if relation=="on":
                relation="on_char"
            if relation=="inside":
                relation="inside_char"
            if relation=="facing_item":
                relation="facing"
            if relation=="close_item":
                relation="close"

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