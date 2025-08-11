import numpy as np
import re
import os
from utils_eval import check_unexplorable

class BaseAgent:
    def __init__(self, config, filepath, task_logger, epoch_path=None, agent_base_type="behavior",evaluation=False):
        self.agent_base_type = agent_base_type
        self.is_evaluation=evaluation

        self.task_name=''
        self.goal_nl=''

        self.config=config
        self.logger=task_logger
        self.name2opid = {}
        self.name2id = {}
        self.opid2name = {}
        self.name2size = {}
        self.num_items = 0 # Record how mani items in the scene
        self.item_type = np.array([], dtype=object) # Record the type of each item
        self.category = {}
        self.properties = {}
        self.relations = {}
        self.state = {}
        self.character_state = {}
        self.exploration = {}

        """
        path to the CDL files
        internal_executable_file_path: the file can be solve py planner: state + goal
        state_file_path: the file contains the current state: state (only)        
        """

        self.internal_executable_file_path = os.path.join(epoch_path,'internal_executable.cdl')
        self.state_file_path = os.path.join(epoch_path,'current_agent_state.cdl')

    def set_human_helper(self,human_helper):
        self.human_helper=human_helper
        self.human_helper.set_name2id(self.name2id)

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

        # Read exploration behavior
        exploration_behavior = re.search(r'#exp_behavior\n(.+?)#exp_behavior_end', content, re.DOTALL)
        if exploration_behavior:
            exploration_behavior = exploration_behavior.group(1)
            self.exploration_behavior = exploration_behavior

        # behavior_from_library = re.search(r'#behaviors_from_library\n(.+?)#behaviors_from_library_end', content, re.DOTALL)
        # if behavior_from_library:
        #     behavior_from_library = behavior_from_library.group(1)
        #     self.behaviors_from_library_representation = behavior_from_library

        # Read goal representation
        goal_rep=re.search(r'#goal_representation\n(.+?)#goal_representation_end', content, re.DOTALL)
        if goal_rep:
            goal_representation_section = goal_rep.group(1)
            self.goal_representation = goal_representation_section
        # if not goal_rep:
        #     print("No goal representation yet")
        # Set uncertain information for unknown items
        if not self.is_evaluation:
            self._set_uncertain_information()
        self.save_to_file()
        self.save_to_file(self.state_file_path)

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
            self.opid2name[op_id] = name
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


    def save_to_file(self,path=None):
        if path is None:
            path = self.internal_executable_file_path

        with open(path, 'w') as file:
            # Write problem and domain
            file.write('problem "agent-problem"\n')
            # Use the same domain name as the evaluator/agent CDL we load (cdl_case_study.cdl)
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

            if path == self.internal_executable_file_path and self.agent_base_type == "behavior":
                file.write("\n#exp_behavior\n")
                file.write(self.exploration_behavior)
                file.write("\n#exp_behavior_end\n")
                # file.write("\n#behaviors_from_library\n")
                # file.write(self.behaviors_from_library_representation)
                # file.write("\n#behaviors_from_library_end\n")
                file.write("\n#goal_representation\n")
                file.write(self.goal_representation)
                file.write("\n#goal_representation_end\n")

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

        if self.is_evaluation:
            state_features.append('used') # this is a trick to make sure the agent can use the object. Only available in evaluation mode

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
    
    def regular_action_obs_update(self, observation):
        """
        update the agent's state based on the observation
        Return: the effects of the action in string
        """
        action_effects = ""
        action_related_objects = []
        for object_name in observation['action'].arguments:
            if object_name.name in self.name2opid:
                action_related_objects.append(object_name.name)

        if len(observation['known'])>0:
            action_effects+="Robot find: "
        for new_known in observation['known']:
            # record those items that are newly known
            if 'character' in new_known:
                continue
            if self.exploration['unknown'][self.name2opid[new_known]]==True:
                self.exploration['unknown'][self.name2opid[new_known]]=False
                action_effects+=f"{new_known}, "
        
                
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

                    if new_relations['relation_type'].lower()=='close':
                        if not check_unexplorable(new_relations['to_name']):
                            action_effects+=f"Robot is close to the {new_relations['to_name']}. "
                    else:
                        action_effects+=f"Robot is {new_relations['relation_type'].lower()} the {new_relations['to_name']}. "

            elif new_relations['to_name']=='char' and new_relations['relation_type']=='ON':
                self.state['on_body'][self.name2opid[new_relations['from_name']]]=True
            else:
                if self.relations[new_relations['relation_type'].lower()][self.name2opid[new_relations['from_name']]][self.name2opid[new_relations['to_name']]]!=True:
                    # means this relation is not already known
                    if new_relations['from_name'] in action_related_objects and new_relations['to_name'] in action_related_objects:
                        action_effects+=f"{new_relations['from_name']} is {new_relations['relation_type'].lower()} {new_relations['to_name']}. "
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
                        if delete_relations['from_name'] in action_related_objects and delete_relations['to_name'] in action_related_objects:
                            action_effects+=f"Robot is no longer {delete_relations['relation_type'].lower()} {delete_relations['to_name']}."
                        self.state[relation_type][self.name2opid[delete_relations['to_name']]]=False
            elif delete_relations['to_name']=='char' and delete_relations['relation_type']=='ON':
                self.state['on_body'][self.name2opid[delete_relations['from_name']]]=False
            else:
                if self.relations[delete_relations['relation_type'].lower()][self.name2opid[delete_relations['from_name']]][self.name2opid[delete_relations['to_name']]]==True:
                    if delete_relations['from_name'] in action_related_objects and delete_relations['to_name'] in action_related_objects:
                        action_effects+=f"{delete_relations['from_name']} is no longer {delete_relations['relation_type'].lower()} {delete_relations['to_name']}."
                    self.relations[delete_relations['relation_type'].lower()][self.name2opid[delete_relations['from_name']]][self.name2opid[delete_relations['to_name']]]=False
        
        for obj_name in observation['states']:
            update_list = observation['states'][obj_name]
            state_change_str = ""

            for update in update_list:
                state_info = update.name.lower()
                # Here we can add descriptive text based on the state transitions
                if state_info == 'clean':
                    if self.state['dirty'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is cleaned. "
                    self.state['clean'][self.name2opid[obj_name]] = True
                    self.state['dirty'][self.name2opid[obj_name]] = False
                elif state_info == 'dirty':
                    if self.state['clean'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} becomes dirty. "
                    self.state['dirty'][self.name2opid[obj_name]] = True
                    self.state['clean'][self.name2opid[obj_name]] = False
                elif state_info == 'open':
                    if self.state['closed'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is opened. "
                    self.state['open'][self.name2opid[obj_name]] = True
                    self.state['closed'][self.name2opid[obj_name]] = False
                elif state_info == 'closed':
                    if self.state['open'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is closed. "
                    self.state['closed'][self.name2opid[obj_name]] = True
                    self.state['open'][self.name2opid[obj_name]] = False
                elif state_info == 'plugged_in':
                    if self.state['unplugged'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is plugged in. "
                    self.state['plugged'][self.name2opid[obj_name]] = True
                    self.state['unplugged'][self.name2opid[obj_name]] = False
                elif state_info == 'plugged_out':
                    if self.state['plugged'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is unplugged. "
                    self.state['unplugged'][self.name2opid[obj_name]] = True
                    self.state['plugged'][self.name2opid[obj_name]] = False
                elif state_info == 'on':
                    if self.state['is_off'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is turned on. "
                    self.state['is_on'][self.name2opid[obj_name]] = True
                    self.state['is_off'][self.name2opid[obj_name]] = False
                elif state_info == 'off':
                    if self.state['is_on'][self.name2opid[obj_name]]==True:
                        state_change_str += f"{obj_name} is turned off. "
                    self.state['is_off'][self.name2opid[obj_name]] = True
                    self.state['is_on'][self.name2opid[obj_name]] = False
                else:
                    print('Error in state updates')
            if obj_name in action_related_objects:
                action_effects+=state_change_str
        # self.report_state('close_char')
        print(action_effects)
        return action_effects
    

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
            knife_id = next((value for key, value in self.name2opid.items() if "knife_" in key), None)
            # knife_id=self.name2opid['knife_2050']
            rh = set(np.where(self.state['holds_rh'] == True)[0])
            lh = set(np.where(self.state['holds_lh'] == True)[0])
            union_indices = rh.union(lh)
            if knife_id in union_indices:
                self.state['cut'][target_id]=True




    # ----------------- Debugging -----------------
    def report_state(self, state_name):
        # report all the related state and object name
        print(f"State: {state_name}")
        for object_name, object_id in self.name2opid.items():
            if self.state[state_name][object_id]==True:
                print(f"{object_name} has {state_name}.")

    def report_relation(self, relation_name, from_name):
        print(f"Relation: {relation_name}")
        for object_name, object_id in self.name2opid.items():
            if self.relations[relation_name][self.name2opid[from_name]][object_id]==True:
                print(f"{object_name} is {relation_name} {from_name}.")
        

    