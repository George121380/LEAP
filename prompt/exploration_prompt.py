import random
import sys
import openai as OpenAI
import re
import numpy as np
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home')
from prompt.relative_obj_prompt import choose_relative_items_prompt
from prompt.ask_GPT import ask_GPT

class TransformationError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
    

def choose_relative_items(goal,unknown=None,additional_information=None,goal_representation=None):
    selected_items=[]
    system="You are an assistant robot with excellent common sense. Now, I need your help to select the items to search for based on the current task and output a list of item serial numbers."
    content=choose_relative_items_prompt(goal,unknown,additional_information,goal_representation)
    # print('=' * 80)
    # print(f"Choose relative items:")
    while True:
        flag=False
        relative_items=ask_GPT(system,content)
        numbers = re.findall(r'\d+', relative_items)
        number_list = list(map(int, numbers))
        # print('=' * 80)
        for item in number_list:
            if item>len(unknown)-1:
                selected_items=[]
                flag=True
                break
            # print(unknown[item])
            selected_items.append(unknown[item])
        if not flag:
            # print('=' * 80)
            return selected_items

def parse_file(file_path):
    objects = []
    categories = {}
    known_objects = set()
    unknown_objects = set()
    binds = {}
    bind_key = None
    name2id = {}
    checked = {}
    id=1
    goal_representation=''
    with open(file_path, 'r') as file:
        section = None
        for line in file:
            line = line.strip()
            if line.startswith('#object_end'):
                section = None
            elif line.startswith('#categories_end'):
                section = None
            elif line.startswith('#'):
                section = line[1:]
                continue
            elif section == 'objects':
                parts = line.split(':')
                if len(parts) == 2:
                    objects.append(parts[0].strip())
                    name2id[parts[0].strip()]=id
                    id+=1
            elif section == 'categories':
                parts = line.split('[')
                if len(parts) == 2:
                    attr, obj = parts
                    obj = obj.split(']')[0]
                    attr = attr.strip()
                    if attr not in categories:
                        categories[attr] = set()
                    categories[attr].add(obj)
            elif line.startswith('known['):
                obj = line.split('[')[1].split(']')[0]
                known_objects.add(obj)
            elif line.startswith('unknown['):
                obj = line.split('[')[1].split(']')[0]
                unknown_objects.add(obj)
            elif line.startswith('checked['):
                obj1, obj2 = line.split('[')[1].split(']')[0].split(',')
                if obj1 not in checked:
                    checked[obj1] = [False]*(len(objects)+1)
                checked[obj1][name2id[obj2]] = True
                
            elif line.startswith('bind '):
                bind_key = line.split()[1].split(':')[0]
            elif bind_key and line.startswith('is_'):
                bind_value = line.split('(')[0].strip()
                binds[bind_key] = bind_value
                bind_key = None
            elif section == 'goal_representation':
                goal_representation+=line
                
        known_objects = set(objects) - unknown_objects
    
    return objects, categories, known_objects, checked, binds, name2id,unknown_objects,goal_representation

def find_unknown_attributes(categories, known_objects, binds):
    unknown_attributes = set()
    required_attributes = set(binds.values())
    for obj,attr in binds.items():
        if attr not in categories:
            raise TransformationError("Error during problem transformation", str("variable not found"))
    for attr, objs in categories.items():
        for obj in objs:
            if obj not in known_objects:
                unknown_attributes.add(attr)
    return list(unknown_attributes & required_attributes)

def find_all_unknown(categories, unknown_objects):
    unknown_attributes = set()
    for attr, objs in categories.items():
        for obj in objs:
            if obj in unknown_objects:
                unknown_attributes.add(attr)
    return list(unknown_attributes)

def random_select_target(categories,unknown_cats,checked,objects,name2id,known_objects):
    target_objs=[]
    posible_locations={}
    for cat in unknown_cats:
        if cat=='is_sink':
            print('debug')
        try_count=0
        while True:
            if try_count>10:
                print(f"failed to find target for {cat}")
                raise TransformationError("Error during problem transformation", str("failed to find target for "+cat))
            ob=random.choice(list(categories[cat]))
            try_count+=1
            ava_known=[]
            if isinstance(checked, np.ndarray):
                for obb in known_objects:
                    if not checked[name2id[ob]][name2id[obb]]:    
                        ava_known.append(obb)
                
                if len(ava_known)==0:
                    if not False in checked[ob]:
                        print(f"{ob} all checked")
                        continue
            else:
                ava_known=known_objects
            target_objs.append(ob)
            posible_locations[ob]=ava_known
            break     
    return target_objs,posible_locations

def get_exp_behavior(goal, additional_information, problem_cdl,checked=None):
    objects, categories, known_objects, _, binds,name2id,unknown_objects,goal_representation = parse_file(problem_cdl)
    # unknown_attributes_needed = find_unknown_attributes(categories, known_objects, binds)
    unknown_attributes_needed = find_all_unknown(categories, unknown_objects)
    if len(unknown_attributes_needed)==0:
        return ''
    unknown_attributes_needed = choose_relative_items(goal, unknown_attributes_needed, additional_information,goal_representation)
    target_objs,locations=random_select_target(categories,unknown_attributes_needed,checked,objects,name2id,known_objects)
    exp_behavior=get_exploration_prompt_template(locations,unknown_attributes_needed,goal,additional_information)
    return exp_behavior

def check_unexplorable(location_name):
    if location_name=='char':
        return True
    location_category='_'.join(location_name.split('_')[:-1])
    unexplorable_list=['room','wall','ceiling','bathroom','bedroom','dining_room','floor']
    return location_category in unexplorable_list

def get_exploration_prompt_template(locations,unknown_attributes_needed,goal,additional_information):
    
    find_info=""
    exp_behavior=''
    if additional_information=='':
        additional_information='No additional information.'
    for obj in locations:
        find_info="""I will provide you with my task objectives and some additional information. Most of this information might be useless, but it could include some location data that may help you find my target item. So please refer to this information and make your own judgment. But remember, your output should only be an integer, and do not analyze or explain the content.\n"""
        find_info+='Your Goal is:'
        find_info+=goal+'\n'
        find_info+='Additional Information:'
        find_info+=additional_information+'\n'
        num=0
        find_info+=f"# Find {obj}:\n"
        find_info+="The possible locations are:\n"
        current_ava_loc_list=[]
        for loc in locations[obj]:
            if check_unexplorable(loc):
                continue
            find_info+=str(num)+". "+loc+"\n"
            current_ava_loc_list.append(loc)
            num+=1
        find_info+="Please only output the number of the most likely position you choose. Do not provide any explanations or comments, just output an integer."
        
        system_prompt="You are an assistant robot with excellent common sense. Now, I need your to tell me the most likely place that I can find the "+obj+"."
        response=ask_GPT(system_prompt,find_info)
        response=re.sub(r'\D', '', response)
        index=int(response)

        target_instance_name='_'.join(obj.split('_')[:-1])
        LLM_chose_loc=current_ava_loc_list[index]

        loc_instance_name='_'.join(LLM_chose_loc.split('_')[:-1])
        loc_instance_id=LLM_chose_loc.split('_')[-1]

        template=f"""
behavior find_{obj}_around_{LLM_chose_loc}({target_instance_name}:item):
    goal: not unknown({target_instance_name})
    body:
        assert is_{target_instance_name}({target_instance_name})
        bind {loc_instance_name}_instance:item where:
            is_{loc_instance_name}({loc_instance_name}_instance) and id[{loc_instance_name}_instance]=={loc_instance_id}
        achieve close_char(char,{loc_instance_name}_instance)
        if can_open({loc_instance_name}_instance):
            achieve_once open({loc_instance_name}_instance)
            exp({target_instance_name},{loc_instance_name}_instance)
        else:
            exp({target_instance_name},{loc_instance_name}_instance)
    eff:
        unknown[{target_instance_name}]=False
        close[{target_instance_name},{loc_instance_name}_instance]=True
        close[{loc_instance_name}_instance,{target_instance_name}]=True
    """
        # print(template)
        exp_behavior+=template+'\n'
    return exp_behavior

if __name__ == '__main__':
    exp_prompt=get_exp_prompt(None,None,"/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/combined_generated.cdl")
    print(exp_prompt)

