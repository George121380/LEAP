# from env_kitchen import Agent,KitchenEnvironment
import sys
import json
import numpy as np
import re
import concepts.dm.crow as crow
import pdb
import os

sys.path.append('embodied-agent-eval/src/VIRTUALHOME/AgentEval-main/virtualhome_eval/simulation/evolving_graph')
sys.path.append('cdl_dataset/scripts')

from experiments.virtualhome.VH_scripts.agent import VHAgent
from utils_eval import get_nodes_information,construct_cdl
from env import VH_Env
from environment import EnvironmentState, EnvironmentGraph
import random
import time

from dataset import parse_file_to_json
from logic_parser import parse_logic_from_file_path
from action_sequence_parser import parse_action_sequence_from_file_path

random.seed(time.time())

class ASTNode:
    pass

class PredicateNode(ASTNode):
    def __init__(self, name):
        self.name = name

class ThenNode(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class OrNode(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

def tokenize(expression): # tokenize the goal_lt expression
    tokens = re.findall(r'\s*(then|or|\(|\)|k\d+)\s*', expression)
    return tokens

def logic_parse(tokens):
    def parse_expression(index):
        node, index = parse_term(index)
        while index < len(tokens) and tokens[index] == 'or':
            index += 1
            right_node, index = parse_term(index)
            node = OrNode(node, right_node)
        return node, index

    def parse_term(index):
        node, index = parse_factor(index)
        while index < len(tokens) and tokens[index] == 'then':
            index += 1
            right_node, index = parse_factor(index)
            node = ThenNode(node, right_node)
        return node, index

    def parse_factor(index):
        token = tokens[index]
        if token == '(':
            index += 1
            node, index = parse_expression(index)
            if tokens[index] != ')':
                raise SyntaxError('Expected )')
            index += 1
            return node, index
        elif re.match(r'k\d+', token):
            node = PredicateNode(token)
            index += 1
            return node, index
        else:
            raise SyntaxError(f'Unexpected token: {token}')

    ast, index = parse_expression(0)
    if index != len(tokens):
        raise SyntaxError('Unexpected tokens at the end')
    return ast

class Evaluator:
    def __init__(self,task_file_path,logger,epoch_path) -> None:
        self.logger=logger
        self.task_file_path=task_file_path
        self.name2opid = {}
        self.name2id = {}
        self.name2size = {}
        self.num_items = 0 # Record how mani items in the scene
        self.item_type = np.array([], dtype=object) # Record the type of each item
        self.category = {}
        self.properties = {}
        self.relations = {}
        self.state = {}
        self.character_state = {}
        self.exploration = {}
        self.init_path="experiments/virtualhome/CDLs/init_scene_NPO.cdl"
        # self.state_file_path = 'experiments/virtualhome/CDLs/evaluator_state.cdl'
        self.state_file_path = os.path.join(epoch_path,'evaluator_state.cdl')
        # self.internal_executable_file_path = 'experiments/virtualhome/CDLs/evaluator_execution.cdl'
        self.internal_executable_file_path = os.path.join(epoch_path,'evaluator_execution.cdl')
        self.basic_domain_knowledge_file_path = 'experiments/virtualhome/CDLs/virtualhome_evaluator.cdl'
        self.init_scene_graph=None
        self.classes=None
        self.load_scene()
        self.env=VH_Env(self.init_scene_graph)
        self._parse_file(self.init_path)
        self.task_data=parse_file_to_json(task_file_path)
        if 'Logic' in self.task_data:
            self.goal_lt=logic_parse(tokenize(self.task_data['Logic'])) # A logic tree used for keystates evaluation
        else:
            self.goal_lt=None
        self.keystates=self.task_data['Keystates']

        if 'Actions' in self.task_data:
            self.required_actions=self.task_data['Actions']
        else:
            self.required_actions=None
        self.keystate_achieved_flag=False
        self.required_actions_achieved_flag=False
        self.wrapped_keystates_func={}
        self.wrap_keystates()
        self.achieved_keystates=set()
        # self.start_counting=self.left_action_counting_for_each_keystate()
        self.end_counting=None
        self.action_completion_rate="No required actions"
        self.Logic=parse_logic_from_file_path(task_file_path)
        self.Action_sequences=parse_action_sequence_from_file_path(task_file_path)

    def load_scene(self)->None:
        scene_path='cdl_dataset/Scene.json'
        with open(scene_path) as f:
            scene=json.load(f)
        init_scene_graph = EnvironmentGraph(scene)
        objects,states,relationships,properties,categories,classes,cat_statement,sizes=get_nodes_information(init_scene_graph,PO=False)
        construct_cdl(self.init_path,objects,states,relationships,properties,cat_statement,sizes)
        self.init_scene_graph=init_scene_graph
        self.classes=classes
    
    def _initialize_relationships(self):
        relationship_features = [
            "on", "inside", "between", 
            "close","facing"
        ]
        for feature in relationship_features:
            self.relations[feature] = np.full((self.num_items , self.num_items ), "uncertain", dtype=object)

    def _initialize_states(self):
        state_features = [
            "is_on", "is_off", "open", "closed", "dirty", 
            "clean", "plugged", "unplugged", "facing_char","on_char", "on_body","close_char", "inside_char","holds_rh", "holds_lh",'has_water','cut','visited','used','inhand'
        ]
        for feature in state_features:
            self.state[feature] = np.full(self.num_items , "uncertain", dtype=object)

    def _initialize_character_states(self):
        self.character_state['standing']=True
        self.character_state['sitting']=False
        self.character_state['lying']=False
        self.character_state['sleeping']=False
        self.character_state['has_a_free_hand']=True

    def _initialize_properties(self):
        property_features = [
            "surfaces", "grabbable", "sittable","lieable","hangable","drinkable","eatable","recipient","cuttable", "pourable", 
            "can_open", "has_switch", "containers", "has_plug", "readable","lookable","is_clothes","is_food","person","body_part","cover_object","has_paper","movable","cream","has_size"
        ]
        for feature in property_features:
            self.properties[feature] = np.full(self.num_items , "uncertain", dtype=object)

    def _parse_file(self, filepath:str):
        with open(filepath, 'r') as file:
            content = file.read()

        # Read IDs and determine the number of items
        id_section = re.search(r'#id\n(.+?)#id_end', content, re.DOTALL).group(1)
        self.num_items = self._parse_id_section(id_section)
        self._initialize_relationships()
        self._initialize_properties()
        self._initialize_states()
        self._initialize_character_states()

        size_section = re.search(r'#sizes\n(.+?)#sizes_end', content, re.DOTALL).group(1)
        self._parse_size_section(size_section)

        # Initialize vectors with None values
        self.item_type = np.full(self.num_items, None, dtype=object)
        known = np.full(self.num_items , False, dtype=bool)
        checked = np.full((self.num_items , self.num_items), False, dtype=bool)
        self.exploration.update({"unknown": known})
        self.exploration.update({"checked": checked})

        # Read objects
        object_section = re.search(r'#objects\n(.+?)#object_end', content, re.DOTALL).group(1)
        self._parse_type_section(object_section)

        # Read categories
        init_section = re.search(r'#categories\n(.+?)#categories_end', content, re.DOTALL).group(1)
        self._parse_categories_section(init_section)

        # Read states
        state_section = re.search(r'#states\n(.+?)#states_end', content, re.DOTALL).group(1)
        self._parse_state_section(state_section)

        # Read char states
        char_section = re.search(r'#char\n(.+?)#char_end', content, re.DOTALL)
        if char_section:
            char_section = char_section.group(1)
            self._parse_char_section(char_section)

        char_state_section = re.search(r'#char_states\n(.+?)#char_states_end', content, re.DOTALL)
        if char_state_section:
            char_state_section = char_state_section.group(1)
            self._parse_char_state_section(char_state_section)

        # Read properties
        property_section = re.search(r'#properties\n(.+?)#properties_end', content, re.DOTALL).group(1)
        self._parse_properties_section(property_section)

        # Read exploration
        exploration_section = re.search(r'#exploration\n(.+?)#exploration_end', content, re.DOTALL).group(1)
        self._parse_exploration_section(exploration_section)

        # Read relations
        relation_section = re.search(r'#relations\n(.+?)#relations_end', content, re.DOTALL).group(1)
        self._parse_relations_section(relation_section)



        # Read exploration behavior
        exploration_behavior = re.search(r'#exp_behavior\n(.+?)#exp_behavior_end', content, re.DOTALL)
        if exploration_behavior:
            exploration_behavior = exploration_behavior.group(1)
            self.exploration_behavior = exploration_behavior

        # Read goal representation
        goal_rep=re.search(r'#goal_representation\n(.+?)#goal_representation_end', content, re.DOTALL)
        if goal_rep:
            goal_representation_section = goal_rep.group(1)
            self.goal_representation = goal_representation_section
        # Set uncertain information for unknown items
        self.save_to_file()
        self.save_to_file(self.internal_executable_file_path)


    def _parse_id_section(self, section:str):
        lines = section.strip().split("\n")
        op_id = 1
        self.name2id['char']=0
        self.name2opid['char']=0
        for line in lines:
            key, value, id_str = re.search(r'(\w+)\[(.+?)\]=(\d+)', line).groups()
            id_num = int(id_str.strip())
            name = f"{value.strip()}"
            if name == 'char':
                continue
            self.name2id[name] = id_num
            self.name2opid[name] = op_id
            op_id += 1
        return op_id
    
    def _parse_size_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value, size_str = re.search(r'(\w+)\[(.+?)\]=(\d+)', line).groups()
                key = key.strip()
                value = value.strip()
                size = size_str.strip()
                self.name2size[value] = size

    def _parse_type_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if line.startswith("#") or line=="":
                continue
            name, type_ = line.split(":")
            name = name.strip()
            if name=="char":
                continue
            type_ = type_.strip()
            obj_id = self.name2opid[name]
            self.item_type[obj_id] = type_

    def _parse_categories_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("[")
                key = key.strip()
                value = value.split("]")[0].strip()
                if not value in self.category:
                    self.category[value]=set()
                self.category[value].add(key)

    def _parse_char_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip().lower() == "true"
                prop_name, obj_name = re.match(r'(\w+)\[(char,.+?)\]', key).groups()
                obj_id = self.name2opid[obj_name]
                
                # Initialize property vector if not already done
                if prop_name not in self.state:
                    new_state = np.full(self.num_items , False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_state_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip().lower() == "true"
                prop_name, obj_name = re.match(r'(\w+)\[(.+?)\]', key).groups()
                obj_id = self.name2opid[obj_name]
                
                # Initialize property vector if not already done
                if prop_name not in self.state:
                    new_state = np.full(self.num_items , False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_char_state_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip().lower() == "true"
                prop_name = re.match(r'(\w+)\[(char)\]', key).groups()
                
                # Initialize property vector if not already done
                if prop_name not in self.state:
                    new_state = np.full(self.num_items , False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.character_state[prop_name] = value

    def _parse_properties_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip().lower() == "true"
                prop_name, obj_name = re.match(r'(\w+)\[(.+?)\]', key).groups()
                obj_id = self.name2opid[obj_name]
                
                # Initialize property vector if not already done
                if prop_name not in self.properties:
                    new_properties = np.full(self.num_items , False, dtype=bool)
                    self.properties.update({prop_name: new_properties})
                
                self.properties[prop_name][obj_id] = value

    def _parse_relations_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line and not 'char' in line:
                key, value = line.split("=")
                key = key.strip()
                relation_name, obj_names = re.match(r'(\w+)\[(.+?)\]', key).groups()
                obj_names = obj_names.split(",")
                obj_ids = [self.name2opid[obj_name.strip()] for obj_name in obj_names]
                relation_value = value.strip().lower() == "true"

                # Initialize matrix for the relation if not already done
                if relation_name not in self.relations:
                    self.relations[relation_name] = np.full((self.num_items , self.num_items ), False, dtype=bool)

                # Set the value for the relation between the objects
                if len(obj_ids) == 2:
                    i, j = obj_ids
                    self.relations[relation_name][i][j] = relation_value
            if '=' in line and 'char' in line:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip().lower() == "true"
                prop_name, obj_name = re.match(r'(\w+)\[(char,.+?)\]', key).groups()
                obj_name=obj_name.split(',')[1]
                obj_id = self.name2opid[obj_name]
                
                # Initialize property vector if not already done
                if prop_name not in self.state:
                    new_state = np.full(self.num_items, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_exploration_section(self, section:str):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("=")
                key = key.strip()
                expstate_name, obj_names = re.match(r'(\w+)\[(.+?)\]', key).groups()
                obj_names = obj_names.split(",")
                obj_ids = [self.name2opid[obj_name.strip()] for obj_name in obj_names]
                relation_value = value.strip().lower() == "true"

                # Initialize matrix for the relation if not already done
                if expstate_name == "unknown":
                    i = obj_ids[0]
                    self.exploration[expstate_name][i] = relation_value

                # Set the value for the relation between the objects
                if expstate_name == "checked":
                    i, j = obj_ids
                    self.exploration[expstate_name][i][j] = relation_value

    def __str__(self):
        properties_str = "\n".join([f"{prop}: {values}" for prop, values in self.properties.items()])
        relations_str = "\n".join([f"{rel}: {pairs}" for rel, pairs in self.relations.items()])
        known_str = "\n".join([f"{i}: {val}" for i, val in enumerate(self.exploration["unknown"]) if val])
        return (f"Name to ID: {self.name2id}\n"
                f"Item Type: {self.item_type}\n"
                f"Initial State: {self.category}\n"
                f"Properties:\n{properties_str}\n"
                f"Relations:\n{relations_str}\n"
                f"unKnown Objects:\n{known_str}")

    def save_to_file(self,path=None):
        if path is None:
            path = self.state_file_path

        with open(path, 'w') as file:
            # Write problem and domain
            file.write('problem "agent-problem"\n')
            file.write('domain "virtualhome_partial.cdl"\n\n')
            file.write("#!pragma planner_is_goal_serializable=False\n")
            file.write("#!pragma planner_is_goal_ordered=True\n")
            file.write("#!pragma planner_always_commit_skeleton=True\n\n")

            # Write objects
            file.write("objects:\n")

            file.write("#objects\n")
            for i, obj_type in enumerate(self.item_type):
                if obj_type:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"  {name}:{obj_type}\n")
            file.write("#object_end\n\n")

            # Write categories (initial state)
            file.write("init:\n    #categories\n")
            for item in self.category:
                for cat in self.category[item]:
                    file.write(f"    {cat}[{item}]=True\n")
            file.write("    #categories_end\n\n")

            # Write states
            file.write("    #states\n")
            for state_name, state_values in self.state.items():
                for i, has_state in enumerate(state_values):
                    if has_state and has_state != "uncertain":
                        if not ("char" in state_name) and not ("hold" in state_name):
                            name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                            file.write(f"    {state_name}[{name}]=True\n")
            file.write("    #states_end\n\n")

            file.write("    #char_states\n")
            for state_name,state_value in self.character_state.items():
                file.write(f"    {state_name}[char]={state_value}\n")
            file.write("    #char_states_end\n\n")

            # Write char states
            file.write("    #char\n")
            for state_name, state_values in self.state.items():
                for i, has_state in enumerate(state_values):
                    if has_state and has_state != "uncertain":
                        if ("char" in state_name) or ("hold" in state_name):
                            name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                            if name!='char':
                                file.write(f"    {state_name}[char,{name}]=True\n")
            file.write("    #char_end\n\n")

            # Write properties
            file.write("    #properties\n")
            for prop_name, prop_values in self.properties.items():
                for i, has_property in enumerate(prop_values):
                    if has_property and has_property != "uncertain":
                        name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                        file.write(f"    {prop_name}[{name}]=True\n")
            file.write("    #properties_end\n\n")

            # Write relations
            file.write("    #relations\n")
            for relation_name, relation_matrix in self.relations.items():
                for i, row in enumerate(relation_matrix):
                    for j, has_relation in enumerate(row):
                        if has_relation and has_relation != "uncertain":
                            name_i = next(name for name, id_ in self.name2opid.items() if id_ == i)
                            name_j = next(name for name, id_ in self.name2opid.items() if id_ == j)
                            file.write(f"    {relation_name}[{name_i},{name_j}]=True\n")
            file.write("    #relations_end\n\n")

            # Write exploration
            file.write("    #exploration\n")
            unknown = self.exploration.get("unknown", [])
            for i, is_unknown in enumerate(unknown):
                if is_unknown:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    
                    file.write(f"    unknown[{name}]=True\n")
            file.write("    #exploration_end\n")

            file.write("\n    #id\n")
            for i, obj_type in enumerate(self.item_type):
                if obj_type:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"    id[{name}]={self.name2id[name]}\n")
            file.write("    #id_end\n")

            file.write("\n    #size\n")
            for i, obj_type in enumerate(self.item_type):
                if obj_type:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    if name in self.name2size:
                        file.write(f"    size[{name}]={self.name2size[name]}\n")
            file.write("    #size_end\n")

    def updates(self,observation):
        if "You can not" in observation:
            return
        # pdb.set_trace()
        if not isinstance(observation, dict):
            print("debug: ",observation)
            return
        if not observation['exp_flag'] and not observation['obs_flag']:# other 
            for new_relations in observation['relations']:# add relations
                if 'character' in new_relations['to_name']:
                    new_relations['to_name']='char'
                if new_relations['from_name']=='char':
                    
                    if new_relations['relation_type']=='HOLDS_LH':
                        if self.state['holds_lh'][self.name2opid[new_relations['to_name']]]!=True:
                            self.state['holds_lh'][self.name2opid[new_relations['to_name']]]=True
                    elif new_relations['relation_type']=='HOLDS_RH':
                        if self.state['holds_rh'][self.name2opid[new_relations['to_name']]]!=True:
                            self.state['holds_rh'][self.name2opid[new_relations['to_name']]]=True
                    else:
                        relation_type=new_relations['relation_type'].lower()+"_char"
                        self.state[relation_type][self.name2opid[new_relations['to_name']]]=True


                elif new_relations['to_name']=='char' and new_relations['relation_type']=='ON':
                    self.state['on_body'][self.name2opid[new_relations['from_name']]]=True
                else:
                    if self.relations[new_relations['relation_type'].lower()][self.name2opid[new_relations['from_name']]][self.name2opid[new_relations['to_name']]]!=True:
                        self.relations[new_relations['relation_type'].lower()][self.name2opid[new_relations['from_name']]][self.name2opid[new_relations['to_name']]]=True

            for delete_relations in observation['remove_relations']:# delete relations
                if 'character' in delete_relations['to_name']:
                    delete_relations['to_name']='char'
                if 'character' in delete_relations['from_name']:
                    delete_relations['from_name']='char'
                if delete_relations['from_name']=='char':
                    if delete_relations['relation_type']=='HOLDS_LH':
                        if self.state['holds_lh'][self.name2opid[delete_relations['to_name']]]==True:
                            self.state['holds_lh'][self.name2opid[delete_relations['to_name']]]=False
                    elif delete_relations['relation_type']=='HOLDS_RH':
                        if self.state['holds_rh'][self.name2opid[delete_relations['to_name']]]==True:
                            self.state['holds_rh'][self.name2opid[delete_relations['to_name']]]=False
                    else:
                        relation_type=delete_relations['relation_type'].lower()+"_char"
                        if self.state[relation_type][self.name2opid[delete_relations['to_name']]]==True:
                            self.state[relation_type][self.name2opid[delete_relations['to_name']]]=False
                elif delete_relations['to_name']=='char' and delete_relations['relation_type']=='ON':
                    self.state['on_body'][self.name2opid[delete_relations['from_name']]]=False
                else:
                    if self.relations[delete_relations['relation_type'].lower()][self.name2opid[delete_relations['from_name']]][self.name2opid[delete_relations['to_name']]]==True:
                        self.relations[delete_relations['relation_type'].lower()][self.name2opid[delete_relations['from_name']]][self.name2opid[delete_relations['to_name']]]=False
            
            for obj_name in observation['states']:
                update_list=observation['states'][obj_name]
                for update in update_list:
                    state_info=update.name.lower()
                    if state_info=='clean':
                        self.state['clean'][self.name2opid[obj_name]]=True
                        self.state['dirty'][self.name2opid[obj_name]]=False
                    elif state_info=='dirty':
                        self.state['dirty'][self.name2opid[obj_name]]=True
                        self.state['clean'][self.name2opid[obj_name]]=False
                    elif state_info=='open':
                        self.state['open'][self.name2opid[obj_name]]=True
                        self.state['closed'][self.name2opid[obj_name]]=False
                    elif state_info=='closed':
                        self.state['closed'][self.name2opid[obj_name]]=True
                        self.state['open'][self.name2opid[obj_name]]=False
                    elif state_info=='plugged_in':
                        self.state['plugged'][self.name2opid[obj_name]]=True
                        self.state['unplugged'][self.name2opid[obj_name]]=False
                    elif state_info=='plugged_out':
                        self.state['unplugged'][self.name2opid[obj_name]]=True
                        self.state['plugged'][self.name2opid[obj_name]]=False
                    elif state_info=='on':
                        self.state['is_on'][self.name2opid[obj_name]]=True
                        self.state['is_off'][self.name2opid[obj_name]]=False
                    elif state_info=='off':
                        self.state['is_off'][self.name2opid[obj_name]]=True
                        self.state['is_on'][self.name2opid[obj_name]]=False
                    else:
                        print('error in state updates')

            # update character state
            if observation['action'].name=='standup_executor':
                self.character_state['standing']=True
                self.character_state['sitting']=False
                self.character_state['lying']=False
                self.character_state['sleeping']=False
            
            if observation['action'].name=='sit_executor':
                self.character_state['standing']=False
                self.character_state['sitting']=True
                self.character_state['lying']=False
                self.character_state['sleeping']=False
            
            if observation['action'].name=='lie_executor':
                self.character_state['standing']=False
                self.character_state['sitting']=False
                self.character_state['lying']=True
                self.character_state['sleeping']=False
            
            if observation['action'].name=='sleep_executor':
                self.character_state['standing']=False
                self.character_state['sitting']=False
                self.character_state['lying']=False
                self.character_state['sleeping']=True

            if observation['action'].name=='grab_executor':
                hold_rl=np.any(self.state['holds_lh']==True)
                hold_rr=np.any(self.state['holds_rh']==True)
                if hold_rl and hold_rr:
                    self.character_state['has_a_free_hand']=False
                self.state['inhand'][self.name2opid[observation['action'].arguments[0].name]]=True
                
            if observation['action'].name=='put_executor' or observation['action'].name=='putin_executor':
                self.character_state['has_a_free_hand']=True
                self.state['inhand'][self.name2opid[observation['action'].arguments[0].name]]=False

            record_action=['switchoff_executor','switchon_executor','put_executor','putin_executor','grab_executor','wash_executor','scrub_executor','rinse_executor','sit_executor','lie_executor','open_executor','close_executor','pour_executor','plugin_executor','plugout_executor','find_executor','turnto_executor','cut_executor','eat_executor','drink_executor','lookat_executor','wipe_executor','puton_executor','putoff_executor','read_executor','touch_executor','type_executor','watch_executor','move_executor','push_executor','pull_executor']
            # update used states
            action=observation['action']
            if action.name in record_action:
                for argument in action.arguments:
                    used_obj_id=self.name2opid[argument.name]
                    self.state['used'][used_obj_id]=True
        self.annotation(observation)
        self.save_to_file()
        self.save_to_file(self.internal_executable_file_path)
        

    def annotation(self,observation):
        if observation['action'].name=='switchon_executor' and 'faucet' in observation['action'].arguments[0].name:
            faucet_id=self.name2opid[observation['action'].arguments[0].name]
            rh = set(np.where(self.state['holds_rh'] == True)[0])
            lh = set(np.where(self.state['holds_lh'] == True)[0])
            close_obj=set(np.where(self.relations['close'][faucet_id] == True)[0])
            container=set(np.where(self.properties['containers'] == True)[0])
            close_containers=close_obj.intersection(container)

            union_indices = rh.union(lh)
            for i in union_indices or close_containers:
                if self.properties['containers'][i]:
                    self.state['has_water'][i]=True

        if observation['action'].name=='cut_executor':
            target_id=self.name2opid[observation['action'].arguments[0].name]
            knife_id=self.name2opid['knife_2050']
            rh = set(np.where(self.state['holds_rh'] == True)[0])
            lh = set(np.where(self.state['holds_lh'] == True)[0])
            union_indices = rh.union(lh)
            if knife_id in union_indices:
                self.state['cut'][target_id]=True
    
    def get_state(self):
        # Get the current CDL state of the agent, "problem" will be used by CDL Solver
        domain = crow.load_domain_file(self.basic_domain_knowledge_file_path)
        problem = crow.load_problem_file(self.internal_executable_file_path, domain=domain)
        return problem

    def check_single_keystate(self,key_state,key_state_representation:str):
        assert key_state_representation != ''
        with open(self.state_file_path, 'r') as file:
            state_content = file.read()
        executable_content = state_content + "\n#goal_representation\n" + key_state_representation + "\n#goal_representation_end\n"
        with open(self.internal_executable_file_path, 'w') as file:
            file.write(executable_content)
        cdl_state = self.get_state()
        plans, stats = crow.crow_regression(
        cdl_state.domain, cdl_state, goal=cdl_state.goal, min_search_depth=12, max_search_depth=12,
        is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True, commit_skeleton_everything=False,
        enable_state_hash=False,
        verbose=False
    )
        if len(plans) == 0:
            print("Evaluator failed to find a plan")
            self.logger.info(self.task_file_path,f'Checking {key_state}',"Evaluator failed to find a plan",'','','')

            return 1e9
        print("State:",len(plans[0]),"steps left")
        left_actions=''
        for action in plans[0]:
            left_actions+=str(action)+';'
        print(key_state," missed actions:",left_actions)
        self.logger.info(self.task_file_path,key_state,f"missed actions: {left_actions}",f'missed action num: {len(plans[0])}','','')

        # print("missed actions:",plans[0])
        return plans[0]
    
    def wrap_keystates(self):
        for key in self.keystates:
            goal_behavior_template=f"""\nbehavior __goal__():\n     body:\n         {key}()"""
            self.wrapped_keystates_func[key]=(self.keystates[key]+goal_behavior_template)

    def calculate_action_completion(self, required_actions, action_history):
            """
            Calculate the completion percentage between required actions and the agent's action history.
            """
            required_len = len(required_actions)
            if required_len == 0:
                return 1.0  # If there are no required actions, consider it fully complete

            # Initialize counters
            matched_actions = 0
            action_history_len = len(action_history)
            action_idx = 0

            for required_action in required_actions:
                # Find the required action in the action history starting from action_idx
                while action_idx < action_history_len:
                    if action_history[action_idx]['action'] == required_action:
                        matched_actions += 1
                        action_idx += 1
                        break
                    action_idx += 1

            completion_percentage = matched_actions / required_len
            return completion_percentage

    def left_action_counting_for_each_keystate(self):
        counting_dict={}
        debug_flag=False
        for keystate in self.keystates:
            print(f"Checking keystate: {keystate}")
            try:
                if keystate in self.achieved_keystates:
                    counting_dict[keystate]=0
                else:
                    result = len(self.check_single_keystate(keystate,self.wrapped_keystates_func[keystate]))
                    counting_dict[keystate]=result
            except Exception as e:
                print(f"Error in checking keystate: {keystate}")
                print(e)
                counting_dict[keystate]=int(1e9)
                debug_flag=True
        if debug_flag:
            print("Some keystates are incorrect")
        else:
            print("All keystates are correct")
        #test
        # self.logger.info(counting_dict,'','','','','')
        return counting_dict
        

    def evaluate_actions(self, action_history):
        """
        Calculate the completion percentage of the required actions.
        """
        # tokens = action_tokenize(self.task_data['Actions'])
        # parser = Parser(tokens)
        # expr = parser.parse()
        # sequences = generate_sequences(expr)
        
        max_completion = 0.0
        for seq in self.Action_sequences:
            completion = self.calculate_action_completion(seq, action_history)
            if completion > max_completion:
                max_completion = completion
            if completion == 1.0:
                break  # No need to check further if fully completed
        return max_completion

    def evaluate_keystates(self,ast,Root=False):
        if Root:
            ast=self.goal_lt
        if isinstance(ast, PredicateNode):
            print("Evaluator is checking",ast.name)
            if ast.name in self.achieved_keystates:
                return True
            result=(len(self.check_single_keystate(ast.name,self.wrapped_keystates_func[ast.name]))==0)
            if result:
                self.achieved_keystates.add(ast.name)
            return result
        elif isinstance(ast, ThenNode):
            return self.evaluate_keystates(ast.left) and self.evaluate_keystates(ast.right)
        elif isinstance(ast, OrNode):
            return self.evaluate_keystates(ast.left) or self.evaluate_keystates(ast.right)
        else:
            raise ValueError('Unknown AST node')
 

    def evaluate(self,ast,action_history,Root=False):
        print('='*60,"Evaluation: Start")
        if not self.keystate_achieved_flag:
            if self.keystates:
                self.keystate_achieved_flag=self.evaluate_keystates(ast,Root)
            else:
                self.keystate_achieved_flag=True
            
        else:
            print("State: Achieved")
                 
        if not self.required_actions_achieved_flag:
            if self.required_actions:
                self.action_completion_rate = self.evaluate_actions(action_history)
                self.required_actions_achieved_flag = self.action_completion_rate == 1.0
                if self.required_actions_achieved_flag:
                    print("Action: Achieved")
                else:
                    print(f"Action Completion Rate: {self.action_completion_rate}")
                    
            else:
                self.required_actions_achieved_flag = True
                self.action_completion_rate = 'No actions required'
        else:
                print("Action: Achieved")
        if self.keystate_achieved_flag and self.required_actions_achieved_flag:
            print("Success")
        print('='*60,"Evaluation: End")
        return self.keystate_achieved_flag and self.required_actions_achieved_flag
    
    def evaluate_final(self,ast,action_history,Root=False):
        evaluate_result=self.evaluate(ast,action_history,Root)
        self.end_counting=self.left_action_counting_for_each_keystate()
        # Calculate the completion rate of each keystate
        complete_rate={}
        complete_rate['Keystate']={}
        # complete_rate['Action']={}
        # for key in self.start_counting:
        #     if self.start_counting[key]==1e9 or self.end_counting[key]==1e9:
        #         complete_rate['Keystate'][key]="Keystate Evaluate Error"
        #         return "Keystate Evaluate Error",None
        #         # continue
        #     if self.start_counting[key]==0 and self.end_counting[key]==0:
        #         complete_rate['Keystate'][key]=1
        #         print(f"Keystate: {key} - Completion Rate: 1")
        #         continue
        
        #     if self.start_counting[key]==0:
        #         complete_rate['Keystate'][key]=0
        #         print(f"Keystate: {key} - Completion Rate: 0")
        #         continue

        #     cr=1-(self.end_counting[key]/self.start_counting[key])
        #     complete_rate['Keystate'][key]=max(cr,0)
        #     print(f"Keystate: {key} - Completion Rate: {complete_rate['Keystate'][key]}")


        complete_rate['Action']=self.action_completion_rate
        # print(f"Action Completion Rate: {complete_rate['Action']}")
        complete_rate_info=''
        for key in self.end_counting:
            complete_rate_info+=f"Keystate: {key} - Requires: {self.end_counting[key]} steps\n"
        complete_rate_info+=f"Action Completion Rate: {complete_rate['Action']}"
        print(complete_rate_info)

        return evaluate_result,complete_rate_info
    
    def complete_single_keystate(self,keystate):
        if keystate in self.achieved_keystates:
            return []
        result=self.check_single_keystate(keystate,self.wrapped_keystates_func[keystate])
        actions=[]
        for action in result:
            actions.append(str(action))
        return result
        
    
if __name__=='__main__':
    task_path='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/cdl_dataset/dataset/Cook_some_food/g4.txt'
    evaluator=Evaluator(task_path)