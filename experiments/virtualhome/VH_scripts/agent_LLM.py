import sys
sys.path.append('prompt')
from ask_GPT import ask_GPT
from baseline_LLM import LLM_Agent_Prompt
import json
import numpy as np
import re
from utils_eval import get_nodes_information,construct_cdl
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class Argument:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Action:
    def __init__(self, executor_string):
        self.executor_string = executor_string
        self.name = None
        self.arguments = []
        self.parse_executor_string()

    def parse_executor_string(self):
        pattern = r'(\w+_executor)\(([^)]*)\)'
        match = re.match(pattern, self.executor_string)
        
        if not match:
            raise ValueError(f"Invalid format: {self.executor_string}")
        
        self.name = match.group(1)
        
        arguments = match.group(2).split(',')
        self.arguments = [Argument(arg.strip()) for arg in arguments]

    def __str__(self):
        return self.executor_string

class LLM_Agent:
    def __init__(self,args,filepath,logger,epoch_path):
        self.args=args
        self.logger=logger
        self.model=SentenceTransformer('paraphrase-MiniLM-L6-v2')  # You can choose other models
        self.scene_info=None
        self.name2opid = {}
        self.name2id = {}
        self.id2name = {}
        self.num_items = 0 # Record how mani items in the scene
        self.item_type = np.array([], dtype=object) # Record the type of each item
        self.category = {}
        self.properties = {}
        self.relations = {}
        self.state = {}
        self.character_state = {}
        self.exploration = {}
        # Task information
        self.task_name=''
        self.goal_nl=''
        self.self_evaluate_num=0
        self.add_info_nl=''
        self.add_info_human_instruction=''
        self.add_info_trial_and_error_info=''
        self.add_info_action_history=[]
        self.add_info_action_history_for_evaluation=[]
        
        """
        path to the CDL files
        internal_executable_file_path: the file can be solve py planner: state + goal
        basic_domain_knowledge_file_path: domain knowledge
        state_file_path: the file contains the current state: state (only)        
        """
        self.internal_executable_file_path = 'experiments/virtualhome/CDLs/internal_executable.cdl'
        self.basic_domain_knowledge_file_path = 'experiments/virtualhome/CDLs/virtualhome_partial.cdl'
        self.state_file_path = 'experiments/virtualhome/CDLs/current_agent_state.cdl'
        self.plan=[]
        self.current_step=0
        self.exp_fail_num=0
        self.error_times=0
        self._parse_file(filepath)
        self.save_to_file()
        self.relavant_objects=[]
        self.relavant_item_info=''
        self.action_counting={}
        self.fail_to_find_dict={}
        self.exp_helper_query_times=0

    def reset_goal(self, goal, taskname):
        self.goal_nl=goal
        self.task_name=taskname
        relavant=self.select_relevant_items()
        self.relavant_objects=relavant

    def set_human_helper(self,human_helper):
        self.human_helper=human_helper
        self.human_helper.set_name2id(self.name2id)

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
            "clean", "plugged", "unplugged", "facing_char","on_char", "on_body","close_char", "inside_char","holds_rh", "holds_lh",'has_water','cut','visited','inhand'
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
            "can_open", "has_switch", "containers", "has_plug", "readable","lookable","is_clothes","is_food","person","body_part","cover_object","has_paper","movable","cream"
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

        # Read char related states
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

        # if not goal_rep:
        #     print("No goal representation yet")
        # Set uncertain information for unknown items
        self._set_uncertain_information()
        self.save_to_file()

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
            self.id2name[op_id] = name
            op_id += 1
        return op_id

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

    def _set_uncertain_information(self:str):
        for obj_id in range(1, self.num_items ):
            if self.exploration["unknown"][obj_id]:
                # For objects that are not known, set properties and relations to "uncertain"
                # for prop_name in self.properties:
                #     self.properties[prop_name][obj_id] = "uncertain"
                for relation_name in self.relations:
                    for i in range(self.num_items):
                        self.relations[relation_name][obj_id][i] = "uncertain"
                        self.relations[relation_name][i][obj_id] = "uncertain"
            # else:
            #     # For known objects, set missing properties/relations explicitly to False
            #     # for prop_name, prop_values in self.properties.items():
            #     #     if prop_values[obj_id] == "uncertain":
            #     #         self.properties[prop_name][obj_id] = False
            #     for state_name, state_values in self.state.items():
            #         if state_values[obj_id] == "uncertain":
            #             self.state[state_name][obj_id] = False
            #     for relation_name, relation_matrix in self.relations.items():
            #         for i in range(self.num_items ):
            #             if self.exploration["unknown"][i]:
            #                 if relation_matrix[obj_id][i] == "uncertain":
            #                     self.relations[relation_name][obj_id][i] = False
            #                 if relation_matrix[i][obj_id] == "uncertain":
            #                     self.relations[relation_name][i][obj_id] = False

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
            path = self.internal_executable_file_path

        with open(path, 'w') as file:
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
    
    def updates(self,observation):
        if "You can not" in observation: # if this action is not executable
            # self.add_info_trial_and_error_info+=(observation+'\n')
            error="You get this error: "+observation+'\n'
            self.add_info_action_history.append(error)

        else:
            action_effects=''
            if not observation['exp_flag'] and not observation['obs_flag']:# other actions
                for new_known in observation['known']:
                    if 'character' in new_known:
                        continue
                    if self.exploration['unknown'][self.name2opid[new_known]]==True:
                        self.exploration['unknown'][self.name2opid[new_known]]=False
                        action_effects+=f"Find {new_known}. "
                        
                for check_place in observation['checked']:
                    if 'character' in check_place:
                        continue
                    self.exploration['checked'][:,self.name2opid[check_place]]=True

                for new_relations in observation['relations']:# add relations
                    if 'character' in new_relations['to_name']:
                        new_relations['to_name']='char'
                    if new_relations['from_name']=='char':
                        
                        if new_relations['relation_type']=='HOLDS_LH':
                            if self.state['holds_lh'][self.name2opid[new_relations['to_name']]]!=True:
                                action_effects+=f"Grabbing {new_relations['to_name']} by left hand. "
                                self.state['holds_lh'][self.name2opid[new_relations['to_name']]]=True
                        elif new_relations['relation_type']=='HOLDS_RH':
                            if self.state['holds_rh'][self.name2opid[new_relations['to_name']]]!=True:
                                action_effects+=f"Grabbing {new_relations['to_name']} by right hand. "
                                self.state['holds_rh'][self.name2opid[new_relations['to_name']]]=True
                        else:
                            relation_type=new_relations['relation_type'].lower()+"_char"
                            self.state[relation_type][self.name2opid[new_relations['to_name']]]=True

                            action_effects+=f"Robot is {new_relations['relation_type'].lower()} {new_relations['to_name']}. "

                    elif new_relations['to_name']=='char' and new_relations['relation_type']=='ON':
                        self.state['on_body'][self.name2opid[new_relations['from_name']]]=True
                    else:
                        if self.relations[new_relations['relation_type'].lower()][self.name2opid[new_relations['from_name']]][self.name2opid[new_relations['to_name']]]!=True:
                            # action_effects+=f"{new_relations['from_name']} is {new_relations['relation_type'].lower()} {new_relations['to_name']}. "
                            self.relations[new_relations['relation_type'].lower()][self.name2opid[new_relations['from_name']]][self.name2opid[new_relations['to_name']]]=True

                for delete_relations in observation['remove_relations']:# delete relations
                    if 'character' in delete_relations['to_name']:
                        delete_relations['to_name']='char'
                    if 'character' in delete_relations['from_name']:
                        delete_relations['from_name']='char'
                    if delete_relations['from_name']=='char':
                        if delete_relations['relation_type']=='HOLDS_LH':
                            if self.state['holds_lh'][self.name2opid[delete_relations['to_name']]]==True:
                                action_effects+=f"{delete_relations['to_name']} released by left hand. "
                                self.state['holds_lh'][self.name2opid[delete_relations['to_name']]]=False
                        elif delete_relations['relation_type']=='HOLDS_RH':
                            if self.state['holds_rh'][self.name2opid[delete_relations['to_name']]]==True:
                                action_effects+=f"{delete_relations['to_name']} released by right hand. "
                                self.state['holds_rh'][self.name2opid[delete_relations['to_name']]]=False
                        else:
                            relation_type=delete_relations['relation_type'].lower()+"_char"
                            if self.state[relation_type][self.name2opid[delete_relations['to_name']]]==True:
                                action_effects+=f"Robot is no longer {delete_relations['relation_type'].lower()} {delete_relations['to_name']}."
                                self.state[relation_type][self.name2opid[delete_relations['to_name']]]=False
                    elif delete_relations['to_name']=='char' and delete_relations['relation_type']=='ON':
                        self.state['on_body'][self.name2opid[delete_relations['from_name']]]=False
                    else:
                        if self.relations[delete_relations['relation_type'].lower()][self.name2opid[delete_relations['from_name']]][self.name2opid[delete_relations['to_name']]]==True:
                            # action_effects+=f"{delete_relations['from_name']} is no longer {delete_relations['relation_type'].lower()} {delete_relations['to_name']}."
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

            if observation['exp_flag']:# exploration
                exp_target=observation['exp_target']
                exp_loc=observation['exp_loc']
                for new_known in observation['known']:
                        if 'character' in new_known:
                            continue
                        if self.exploration['unknown'][self.name2opid[new_known]]==True:
                            self.exploration['unknown'][self.name2opid[new_known]]=False
                            self.newfind=True # find sth new
                
                for check_place in observation['checked']:
                    self.exploration['checked'][:,self.name2opid[check_place]]=True

                if exp_target in observation['known'] or not self.exploration['unknown'][self.name2opid[exp_target]]:
                    print(f'{exp_target} is successfully explored around {exp_loc} or already known before')
                    action_effects+=f"Find {exp_target}. "
                else:
                    if self.exp_fail_num==5:
                        human_answer=self.query_human(f'Can you help me to find {exp_target} ?')
                        print(f'Query human about the location of {exp_target}.')
                        self.exp_fail_num=0
                        self.add_info_human_instruction+=human_answer+'\n'
                        self.logger.info("","","",self.add_info_nl,"","")

                    self.exp_fail_num+=1
                    print(f'{exp_target} is not around {exp_loc}, re-explore')
                    action_effects+=f"Failed to find {exp_target} around {exp_loc}. "
                    self.save_to_file()
                    

            if observation['obs_flag']:
                obs_target=observation['obs_target']
                self.state['visited'][self.name2opid[obs_target]]=True
                for new_known in observation['known']:
                    if 'character' in new_known:
                        continue
                    if self.exploration['unknown'][self.name2opid[new_known]]==True:
                        self.exploration['unknown'][self.name2opid[new_known]]=False
                        # self.newfind=True # find sth new
                
                for check_place in observation['checked']:
                    if 'character' in check_place:
                        continue
                    self.exploration['checked'][:,self.name2opid[check_place]]=True

                # obs_information=self.obs_query(observation['obs_target'],observation['obs_result'],observation['question'])+'\n'# Query LLM
                obs_information=self.organize_obs_result(observation['obs_result']) # Use observation information directly
                action_effects+=f"Get this information: {obs_information}"

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

            self.annotation(observation)
            self.add_info_action_history.append({'action':str(observation['action']),'effects':action_effects})
            self.add_info_action_history_for_evaluation.append({'action':str(observation['action']),'effects':action_effects})
            self.logger.info("","",str(observation['action']),action_effects,"","")

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

    def query_human(self,question:str):
        record='Record from func query_human in agent.py\n'
        record+=f'Question: {question}\n'
        answer=self.human_helper.QA(question)
        record+=f'Answer: {answer}\n'
        self.logger.info("","","","",record,"")
        return answer
    
    def select_relevant_items(self, k=30):
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # You can choose other models
        task_instruction = self.goal_nl
        task_embedding = model.encode([task_instruction])  # Convert task instruction to vector
        item_list=list(self.name2opid.keys()) # Get all item names
        item_embeddings = model.encode(item_list)          # Convert each item name to vector
        
        similarities = cosine_similarity(task_embedding, item_embeddings)[0]  # 1D array of similarities
        
        # Step 4: Sort items by similarity and select top k
        top_k_indices = np.argsort(similarities)[-k:][::-1]  # Indices of top k most similar items
        top_k_items = [item_list[i] for i in top_k_indices]  # Get the corresponding item names
        self.relavant_objects=top_k_items

    def item_infoto_nl(self):
        self.select_relevant_items()
        description = ""

        for item_name in self.relavant_objects:
            item_id = self.name2opid[item_name]
            description += f"Item name: {item_name}\n"
            
            properties = [prop_name.replace('_', ' ') for prop_name, prop_values in self.properties.items() if prop_values[item_id]==True]
            if properties:
                description += f"  Properties: {'; '.join(properties)}.\n"
            else:
                description += "  Properties: None.\n"
            
            states = [state_name.replace('_', ' ') for state_name, state_values in self.state.items() if state_values[item_id]==True]
            if states:
                description += f"  States: {'; '.join(states)}.\n"
            
            
            relations = []
            for relation_name, relation_matrix in self.relations.items():
                for other_id, has_relation in enumerate(relation_matrix[item_id]):
                    if has_relation==True:
                        other_name = self.id2name[other_id]
                        relations.append(f"{relation_name.replace('_', ' ')} {other_name}")

            if relations:
                description += f"  Relations: {'; '.join(relations)}.\n"

            if not relations and not states:
                description += "  The item is not find yet.\n"
            
                
            description += "\n"
        with open('scene_graph_to_nl.txt','w') as f:
            f.write(description)
        self.relavant_item_info=description
        return description

    def act(self):
        unknown_check=[]

        human_exp_guidance=''

        for action_str, count in self.action_counting.items():
            if count > 10:
                print("Debug: repeat an action for more than 10 times")
                return 'Failed', None
        if len(self.add_info_action_history)>50:
            print("Debug: more than 50 actions have been executed")
            return 'Failed',None
        
        try_times=0
        char_information=''
        lh_hold=np.where(self.state['holds_lh']==True)[0]
        rh_hold=np.where(self.state['holds_rh']==True)[0]
        
        if len(lh_hold)>0:
            for lh in lh_hold:
                char_information+=f'Robot is holding {self.id2name[lh]} by left hand. '
        
        if len(rh_hold)>0:
            for rh in rh_hold:
                char_information+=f'Robot is holding {self.id2name[rh]} by right hand. '

        if not len(lh_hold)>0 and not len(rh_hold)>0:
            char_information+="Robot's arms are empty."

        while True:
            try:
                try_times+=1
                if try_times>10:
                    print("Debug: auto debug for more than 10 times")
                    return 'Failed',None
                content=LLM_Agent_Prompt(self.goal_nl,self.add_info_nl,self.relavant_item_info,self.add_info_action_history,unknown_check,char_information,human_exp_guidance)
                unknown_check=[] # reset unknown_check
                system='I need you to help me output the next action based on the information I provide.'
                response=ask_GPT(system,content)
                action=Action(response)

                wrong_obj_flag=False
                for involved_obj in action.arguments:
                    obj_name=involved_obj.name
                    if not obj_name in self.name2opid:
                        wrong_obj_flag=True
                        break

                    obj_id=self.name2opid[obj_name]
                    if self.exploration['unknown'][obj_id]:
                        unknown_check.append(obj_name)
                        if obj_id in self.fail_to_find_dict:
                            self.fail_to_find_dict[obj_id]+=1
                            if self.fail_to_find_dict[obj_id]>5:
                                answer=f'To find {obj_name}, the human give you this guidance:\n'
                                answer+=self.query_human(f'Can you help me to find {obj_name} ?')
                                human_exp_guidance+=answer+'\n'
                                self.exp_helper_query_times+=1

                        else:
                            self.fail_to_find_dict[obj_id]=1

                if len(unknown_check)>0 or wrong_obj_flag:
                    continue

                if action.name=='grab_executor':
                    # robot can not grab an item by two hands at the same time
                    if self.state['inhand'][self.name2opid[action.arguments[0].name]]==True:
                        continue
                if str(action) in self.action_counting:
                    self.action_counting[str(action)]+=1
                else:
                    self.action_counting[str(action)]=1
                return action,None
            except:
                unknown_check=[]
                continue