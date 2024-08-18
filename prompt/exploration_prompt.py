import random
import sys
import openai as OpenAI
import re
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
    print('=' * 80)
    print(f"Choose relative items:")
    relative_items=ask_GPT(system,content)
    numbers = re.findall(r'\d+', relative_items)
    number_list = list(map(int, numbers))
    print('=' * 80)
    for item in number_list:
        print(unknown[item])
        selected_items.append(unknown[item])
    print('=' * 80)
    

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
        try_count=0
        while True:
            if try_count>10:
                print(f"failed to find target for {cat}")
                raise TransformationError("Error during problem transformation", str("failed to find target for "+cat))
            ob=random.choice(list(categories[cat]))
            try_count+=1
            ava_known=[]
            for obb in known_objects:
                if ob in checked:
                    if not checked[ob][name2id[obb]]:
                        ava_known.append(obb)
                else:
                    ava_known.append(obb)
                
            if len(ava_known)==0:
                if not False in checked[ob]:
                    print(f"{ob} all checked")
                    continue
            target_objs.append(ob)
            posible_locations[ob]=ava_known
            break     
    return target_objs,posible_locations

def get_exp_behavior(goal, additional_information, problem_cdl):
    objects, categories, known_objects, checked, binds,name2id,unknown_objects,goal_representation = parse_file(problem_cdl)
    # unknown_attributes_needed = find_unknown_attributes(categories, known_objects, binds)
    unknown_attributes_needed = find_all_unknown(categories, unknown_objects)
    unknown_attributes_needed = choose_relative_items(goal, unknown_attributes_needed, additional_information,goal_representation)
    target_objs,locations=random_select_target(categories,unknown_attributes_needed,checked,objects,name2id,known_objects)
    exp_behavior=get_exploration_prompt_template(locations,unknown_attributes_needed)
    return exp_behavior
    
def get_exploration_prompt_gpt(locations,unknown_attributes_needed):
    
    find_info=""
    for obj in locations:
        find_info+=f"# Find {obj}:\n"
        find_info+="The possible locations are:\n"
        for loc in locations[obj]:
            find_info+="- "+loc+"\n"

    prompt="""
## Task Instructions:
I have some items that I need to find. Based on the grammar rules I provide, I need you to design a series of formal representations of search actions. I will give you the possible theoretical locations of each item. You need to use your common sense to determine the most possible locations of each item.
Please note that the states, relationships, properties, and keywords you use must not exceed the scope I provided. If you call any function, make sure that you defined them already. Please check these problems carefully before outputting, otherwise the program will not run.

## Find instructions:
Following are the items that you need to find and their possible locations:
"""+find_info+"""

## The available states are (The text following the hash symbol is a comment):
- on(x: item, y: item)
- inside(x: item, y: item)
- close(x: item, y: item)
- close_char(x: character, y: item)
- id[x:item]->int
Here are a easily confusing usage to note:
In states with the _char suffix, the first parameter must always be a "char".

## Syntax rules and keywords:
"char" is a constant instance that represents a character(youself). And character is a basic type, which can only be used when defining a instance. When passing parameters, use "char" uniformly. When defining a variable and specifying its type, use "character".

The following is a template for the behavior of finding items. In the template, you must at least include the following five keywords: behavior, goal, body, achieve, eff.

## Template:
behavior find_a_i_xx_b_j(a:item):
    goal: not unknown(a_i)
    body:
        assert is_a(a_i)
        bind bj:item where:
            is_b(bj) and id[bj]==j
        achieve close_char(char,bj)
        if can_open(bj):
            if can_open(
            achieve open(bj)
    eff:
        foreach o: item:
            if is_a(o):
                unknown[o]=False
                ...

Explaination:
In the template, a_i represents the item to be found, and b_j represents the location where a_i is most likely to appear. Here, a and b are categories of items, and i and j are item numbers. xx is the relationship between a_i and b_j. The goal is fixed: known(a_i). In the body, firstly you need to make sure that a_i belong to category a. So firstly, you need to give a "assert" statement. Then you need to use your common sense to think about how to find a_i in b_j. You need to use achieve to clarify your method. In the eff section, to ensure the correctness of the program execution, eff must be applied to all items of category a, setting their unknown state to False. Additionally, you need to provide the possible relationship between b_j and a based on common sense. And note that you must use [] when calling id[].

For assert statement, please note that in a_i, i is the number, and a refers to all parts except the numeric identifier. Do not omit anything. For example, for clothes_scarf_2019, you should use assert is_clothes_scarf(clothes_scarf2019). Similarly, for food_food_46, you should use assert is_food_food(food_food46).

The following are the descriptions and requirements for each keyword.

# goal
# Usage: Specifies the goal for a behavior. For this task, the goal can only be "not unknown(target)", where target is the item you are looking for.
Example: goal: not unknown(door)

# body
# Usage: In the body, you need to define some achieve statements based on your search method.
body:
    achieve close_char(char,stove_19)

# assert
# Usage: Assert that the item is of the specified type.
Example: assert is_door(door)

# bind
# Usage: Select any item that meets the conditions and assign it to the specified variable. In this task, categories and IDs are usually used to specify particular items.
Example: 
bind oil9:item where:
    is_oil(oil9) and id[oil9]==9

# achieve
# Usage: Specifies the state that needs to be achieved. Only states can follow achieve, not types, variable names, or other unchangeable content. In the current task, you only need to use achieve open(x) and achieve close_char(char,x).The first parameter of close_char must be written as "char", and cannot be anything else.
Example:
achieve close_char(char,fridge18)
achieve open(fridge18)

# eff
# Usage: Represents the effect of an behavior. In this section, perform a series of bool assignments. Note that you should use [] instead of () here. unknown[target]=False must be included in eff, and you also need to explain the relationship between a(target object) and b(location) based on your assumptions and common sense. To ensure the correctness of the program execution, eff must be applied to all items of category a, setting their unknown state to False. Additionally, you need to provide the possible relationship between b_j and a based on common sense. Be careful that you only need to consider the relationship between the target object and the location, and do not need to consider the relationship between the target object and characters.

# behavior
# Usage: One form to represent this, with all keywords and statements included in the behavior
    
## Example:
When you need to:
# Find egg_7:
The possible locations are:
- sink_20
- faucet_21
- fridge_18
- countertop_23
- stove_19
- tomato_2
- bacon_28
- bowl_14
- bowl_15
## Find knife_17:
The possible locations are:
- stove_19
- oven_39
- garlic_36
- countertop_23
- plate_40
- fridge_18

Example analysis:
With your common sense, to find the egg, the most possible location in "possible locations" is the fridge_18. And to find the knife_17, the most possible location in "possible locations" is the also the countertop_23. So you can write these behaviors:

behavior find_egg_7_in_fridge_18(egg7:item):
    goal: not unknown(egg7)
    body:
        assert is_egg(egg7)
        bind fridge18:item where:
            is_fridge(fridge18) and id[fridge18]==18
        achieve close_char(char,fridge18)
        if can_open(fridge18):
            achieve open(fridge18)
    eff:
        foreach o:item:
            if is_egg(item):
                unknown[o] = False
                inside[o,fridge18] = True
        

behavior find_knife_17_in_countertop_23(knife17:item):
    goal: not unknown(knife17)
    body:
        assert is_knife(knife17) 
        bind countertop23:item where:
            is_countertop(countertop23) and id[countert23]==23
        achieve close_char(char,countertop23)
    eff:
        foreach o:item:
            if is_knife(o):
                unknown[o] = False
                on[o,countertop23] = True

## Output Format:
You can only output the description of the converted goal and additional information. Do not include any explanation or any other symbols.
"""
    return prompt

def check_unexplorable(location_name):
    if location_name=='char':
        return True
    location_category='_'.join(location_name.split('_')[:-1])
    unexplorable_list=['room','wall','ceiling','bathroom','bedroom','dining_room','floor']
    return location_category in unexplorable_list


def get_exploration_prompt_template(locations,unknown_attributes_needed):
    
    find_info=""
    exp_behavior=''
    for obj in locations:
        find_info=''
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
        bind {loc_instance_name}:item where:
            is_{loc_instance_name}({loc_instance_name}) and id[{loc_instance_name}]=={loc_instance_id}
        achieve close_char(char,{loc_instance_name})
        if can_open({loc_instance_name}):
            if can_open({loc_instance_name}):
                achieve_once open({loc_instance_name})
                achieve_once closed({loc_instance_name})
    eff:
        foreach o: item:
            if is_{target_instance_name}(o):
                unknown[o]=False
                close[o,{loc_instance_name}]=True
                close[{loc_instance_name},o]=True
                if can_open({loc_instance_name}):
                    inside[o,{loc_instance_name}]=True
    """
        # print(template)
        exp_behavior+=template+'\n'
    return exp_behavior

if __name__ == '__main__':
    exp_prompt=get_exp_prompt(None,None,"/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/combined_generated.cdl")
    print(exp_prompt)

