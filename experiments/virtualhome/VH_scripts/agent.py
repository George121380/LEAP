import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq')
import concepts.dm.crow as crow
import numpy as np
import re
from experiments.virtualhome.VH_scripts.planning import VH_pipeline

class VHAgent:
    def __init__(self, filepath):
        self.name2opid = {}
        self.name2id = {}
        self.num_items = 0
        self.item_type = np.array([], dtype=object)
        self.category = np.array([], dtype=object)
        self.properties = {}
        self.relations = {}
        self.state = {}
        self.exploration = {}
        self.exploration_behavior = ""
        self.goal_representation = ""
        self.internal_state_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/virtualhome_agent_internal_state.cdl'
        self.domain_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/virtualhome_partial.cdl'
        self._parse_file(filepath)
        self.save_to_file()

    def _initialize_relationships(self):
        relationship_features = [
            "on", "inside", "between", 
            "close","facing"
        ]
        for feature in relationship_features:
            self.relations[feature] = np.full((self.num_items + 1, self.num_items + 1), "uncertain", dtype=object)

    def _initialize_states(self):
        state_features = [
            "is_on", "is_off", "open", "closed", "dirty", 
            "clean", "plugged", "unplugged", "facing_char","on_char", "on_body","close_char", "inside_char","holds_rh", "holds_lh"
        ]
        for feature in state_features:
            self.state[feature] = np.full(self.num_items + 1, "uncertain", dtype=object)

    def _initialize_properties(self):
        property_features = [
            "surfaces", "grabbable", "sittable","lieable","hangable","drinkable","eatable","recipient","cuttable", "pourable", 
            "can_open", "has_switch", "containers", "has_plug", "readable","lookable","clothes","person","body_part","cover_object","has_paper","movable","cream"
        ]
        for feature in property_features:
            self.properties[feature] = np.full(self.num_items + 1, "uncertain", dtype=object)

    def _parse_file(self, filepath):
        with open(filepath, 'r') as file:
            content = file.read()

        # Read IDs and determine the number of items
        id_section = re.search(r'#id\n(.+?)#id_end', content, re.DOTALL).group(1)
        self.num_items = self._parse_id_section(id_section)
        self._initialize_relationships()
        self._initialize_properties()
        self._initialize_states()

        # Initialize vectors with None values
        self.item_type = np.full(self.num_items + 1, None, dtype=object)
        self.category = np.full(self.num_items + 1, None, dtype=object)
        known = np.full(self.num_items + 1, False, dtype=bool)
        checked = np.full((self.num_items + 1, self.num_items + 1), False, dtype=bool)
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

        # Read properties
        property_section = re.search(r'#properties\n(.+?)#properties_end', content, re.DOTALL).group(1)
        self._parse_properties_section(property_section)

        # Read relations
        relation_section = re.search(r'#relations\n(.+?)#relations_end', content, re.DOTALL).group(1)
        self._parse_relations_section(relation_section)

        # Read exploration
        exploration_section = re.search(r'#exploration\n(.+?)#exploration_end', content, re.DOTALL).group(1)
        self._parse_exploration_section(exploration_section)

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
        if not goal_rep:
            print("No goal representation yet")
        # Set uncertain information for unknown items
        self._set_uncertain_information()
        self.save_to_file()
        self.save_to_file("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/current_agent_state.cdl")

    def _parse_id_section(self, section):
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

    def _parse_type_section(self, section):
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

    def _parse_categories_section(self, section):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("[")
                key = key.strip()
                value = value.split("]")[0].strip()
                obj_id = self.name2opid[value]
                self.category[obj_id] = key

    def _parse_char_section(self, section):
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
                    new_state = np.full(self.num_items + 1, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_state_section(self, section):
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
                    new_state = np.full(self.num_items + 1, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_properties_section(self, section):
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
                    new_properties = np.full(self.num_items + 1, False, dtype=bool)
                    self.properties.update({prop_name: new_properties})
                
                self.properties[prop_name][obj_id] = value

    def _parse_relations_section(self, section):
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
                    self.relations[relation_name] = np.full((self.num_items + 1, self.num_items + 1), False, dtype=bool)

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
                    new_state = np.full(self.num_items + 1, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_exploration_section(self, section):
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

    def _set_uncertain_information(self):
        for obj_id in range(1, self.num_items + 1):
            if not self.exploration["unknown"][obj_id]:
                # For objects that are not known, set properties and relations to "uncertain"
                # for prop_name in self.properties:
                #     self.properties[prop_name][obj_id] = "uncertain"
                for relation_name in self.relations:
                    for i in range(self.num_items + 1):
                        self.relations[relation_name][obj_id][i] = "uncertain"
                        self.relations[relation_name][i][obj_id] = "uncertain"
            else:
                # For known objects, set missing properties/relations explicitly to False
                # for prop_name, prop_values in self.properties.items():
                #     if prop_values[obj_id] == "uncertain":
                #         self.properties[prop_name][obj_id] = False
                for state_name, state_values in self.state.items():
                    if state_values[obj_id] == "uncertain":
                        self.state[state_name][obj_id] = False
                for relation_name, relation_matrix in self.relations.items():
                    for i in range(self.num_items + 1):
                        if self.exploration["unknown"][i]:
                            if relation_matrix[obj_id][i] == "uncertain":
                                self.relations[relation_name][obj_id][i] = False
                            if relation_matrix[i][obj_id] == "uncertain":
                                self.relations[relation_name][i][obj_id] = False

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
            path = self.internal_state_path

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
            for i, category in enumerate(self.category):
                if category:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"    {category}[{name}]=True\n")
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

            # Write char states
            file.write("    #char\n")
            for state_name, state_values in self.state.items():
                for i, has_state in enumerate(state_values):
                    if has_state and has_state != "uncertain":
                        if ("char" in state_name) or ("hold" in state_name):
                            name = next(name for name, id_ in self.name2opid.items() if id_ == i)
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
            
            checked = self.exploration.get("checked", [])
            for i, row in enumerate(checked):
                for j, is_checked in enumerate(row):
                    if is_checked and is_checked != "uncertain":
                        if i==0 or j==0:
                            continue
                        name_i = next(name for name, id_ in self.name2opid.items() if id_ == i)
                        name_j = next(name for name, id_ in self.name2opid.items() if id_ == j)
                        file.write(f"    checked[{name_i},{name_j}]=True\n")
            file.write("    #exploration_end\n")

            file.write("\n    #id\n")
            for i, obj_type in enumerate(self.item_type):
                if obj_type:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"    id[{name}]={self.name2id[name]}\n")
            file.write("    #id_end\n")

            if path == self.internal_state_path:
                file.write("\n#exp_behavior\n")
                file.write(self.exploration_behavior)
                file.write("\n#exp_behavior_end\n")
                file.write("\n#goal_representation\n")
                file.write(self.goal_representation)
                file.write("\n#goal_representation_end\n")

    def updates(self,observation):
        update_exploration=observation['exploration']
        self.exploration['known']+=update_exploration['known']
        self.exploration['checked']+=update_exploration['checked']
        for state_name, state_values in observation['state'].items():
            for item_id, value in state_values:
                self.state[state_name][item_id] = value

        # Update relations
        for relation_name, relation_values in observation['relations'].items():
            for item_id, target_id, value in relation_values:
                self.relations[relation_name][item_id][target_id] = value
        self.save_to_file()
        self.save_to_file("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/current_agent_state.cdl")

        return update_exploration

    def get_state(self):
        # self.save_to_file()
        # self.save_to_file("current_env_state.cdl")

        
        domain = crow.load_domain_file(self.domain_path)
        problem = crow.load_problem_file(self.internal_state_path, domain=domain)
        return problem


    def act(self):
        cdl_state = self.get_state()
        plans, stats = crow.crow_regression(
        cdl_state.domain, cdl_state, goal=cdl_state.goal, min_search_depth=5, max_search_depth=8,
        is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True,
        enable_state_hash=False,
        verbose=False
    )
        if len(plans) == 0:
                print('No plan found.')
                return None,None
        plan = plans[0]
        if len(plan) == 0:
            print('No plan found.')
            return None,None
            
        action = plan[0]
        return action,plan
    
    def reset_goal(self,goal,additional_information,classes,First_time=False):
        # self.goal_representation=pipeline(goal,additional_information,loop=False,First_time=First_time)
        _,self.goal_representation,self.exploration_behavior=VH_pipeline(goal,additional_information,classes)
        self.save_to_file()
        self.save_to_file("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/current_agent_state.cdl")

        


class VirtualhomeEnvironment:
    def __init__(self, filepath):
        self.name2id = {}
        self.name2opid = {}
        self.num_items = 0
        self.item_type = np.array([], dtype=object)
        self.category = np.array([], dtype=object)
        self.properties = {}
        self.relations = {}
        self.exploration = {}
        self.state={}
        self.goal_representation = ""
        self.internal_state_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/env_internal_state.cdl'
        self.domain_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/virtualhome_partial.cdl'
        self._parse_file(filepath)
        # self.agent=Agent(filepath)
        self.agent_has_a_free_hand = True
        self.save_to_file()

        
    def _initialize_relationships(self):
        relationship_features = [
            "on", "inside", "between", 
            "close"
        ]
        for feature in relationship_features:
            self.relations[feature] = np.full((self.num_items + 1, self.num_items + 1), False, dtype=bool)

    def _initialize_states(self):
        state_features = [
            "is_on", "is_off", "open", "closed", "dirty", 
            "clean", "plugged", "unplugged", "facing_char","on_char", "on_body","close_char", "inside_char","holds_rh", "holds_lh","unknown","checked,facing"
        ]
        for feature in state_features:
            self.state[feature] = np.full(self.num_items + 1, False, dtype=bool)

    def _initialize_properties(self):
        property_features = [
            "surfaces", "grabbable", "sittable","lieable","hangable","drinkable","eatable","recipient","cuttable", "pourable", 
            "can_open", "has_switch", "containers", "has_plug", "readable","lookable","clothes","person","body_part","cover_object","has_paper","movable","cream"
        ]
        for feature in property_features:
            self.properties[feature] = np.full(self.num_items + 1, False, dtype=bool)

    def _parse_file(self, filepath):
        with open(filepath, 'r') as file:
            content = file.read()

        # Read IDs and determine the number of items
        id_section = re.search(r'#id\n(.+?)#id_end', content, re.DOTALL).group(1)
        self.num_items = self._parse_id_section(id_section)
        self._initialize_relationships()
        self._initialize_properties()
        self._initialize_states()


        # Initialize vectors with None values
        self.item_type = np.full(self.num_items + 1, None, dtype=object)
        self.category = np.full(self.num_items + 1, None, dtype=object)
        unknown = np.full(self.num_items + 1, None, dtype=bool)
        checked = np.full((self.num_items + 1, self.num_items + 1), None, dtype=bool)
        self.exploration.update({"unknown": unknown})
        self.exploration.update({"checked": checked})

        # Read objects
        object_section = re.search(r'#objects\n(.+?)#object_end', content, re.DOTALL).group(1)
        self._parse_type_section(object_section)

        # Read categories
        init_section = re.search(r'categories\n(.+?)#categories_end', content, re.DOTALL).group(1)
        self._parse_categories_section(init_section)

        # Read states
        state_section = re.search(r'#states\n(.+?)#states_end', content, re.DOTALL).group(1)
        self._parse_state_section(state_section)

        #read char states
        char_section = re.search(r'#char\n(.+?)#char_end', content, re.DOTALL)
        if char_section:
            char_section = char_section.group(1)
            self._parse_char_section(char_section)


        # Read properties
        property_section = re.search(r'#properties\n(.+?)#properties_end', content, re.DOTALL).group(1)
        self._parse_properties_section(property_section)

        # Read relations
        relation_section = re.search(r'#relations\n(.+?)#relations_end', content, re.DOTALL).group(1)
        self._parse_relations_section(relation_section)

        # Read exploration
        exploration_section = re.search(r'#exploration\n(.+?)#exploration_end', content, re.DOTALL).group(1)
        self._parse_exploration_section(exploration_section)

        # goal_representation
        goal_rp=re.search(r'#goal_representation\n(.+?)#goal_representation_end', content, re.DOTALL)
        if goal_rp:
            goal_representation_section = goal_rp.group(1)
            self.goal_representation = goal_representation_section

    def _parse_id_section(self, section):
        lines = section.strip().split("\n")
        self.name2id['char']=0
        self.name2opid['char']=0
        op_id = 1
        for line in lines:
            key, value, id_str = re.search(r'(\w+)\[(.+?)\]=(\d+)', line).groups()
            id_num = int(id_str.strip())
            name = f"{value.strip()}"
            if name=='char':
                continue
            self.name2id[name] = id_num
            self.name2opid[name] = op_id
            op_id += 1
        return op_id

    def _parse_type_section(self, section):
        lines = section.strip().split("\n")
        for line in lines:
            if line.startswith("#") or line == "":
                continue
            name, type_ = line.split(":")
            name = name.strip()
            if name=='char':
                continue
            type_ = type_.strip()
            obj_id = self.name2opid[name]
            self.item_type[obj_id] = type_

    def _parse_categories_section(self, section):
        lines = section.strip().split("\n")
        for line in lines:
            if "=" in line:
                key, value = line.split("[")
                key = key.strip()
                value = value.split("]")[0].strip()
                obj_id = self.name2opid[value]
                self.category[obj_id] = key

    def _parse_char_section(self, section):
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
                    new_state = np.full(self.num_items + 1, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_state_section(self, section):
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
                    new_state = np.full(self.num_items + 1, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_properties_section(self, section):
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
                    new_properties = np.full(self.num_items + 1, False, dtype=bool)
                    self.properties.update({prop_name: new_properties})
                
                self.properties[prop_name][obj_id] = value

    def _parse_relations_section(self, section):
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
                    self.relations[relation_name] = np.full((self.num_items + 1, self.num_items + 1), False, dtype=bool)

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
                    new_state = np.full(self.num_items + 1, False, dtype=bool)
                    self.state.update({prop_name: new_state})
                
                self.state[prop_name][obj_id] = value

    def _parse_exploration_section(self, section):
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
        return (f"Name to ID: {self.name2id}\n"
                f"item_type: {self.item_type}\n"
                f"Initial State: {self.category}\n"
                f"Properties: {self.properties}\n"
                f"Relations: {self.relations}")

    def save_to_file(self):
        with open(self.internal_state_path, 'w') as file:
            # Write problem and domain (if necessary)
            file.write('problem "kitchen-problem"\n')
            file.write('domain "virtualhome_partial.cdl"\n\n')
            file.write("#!pragma planner_is_goal_serializable=False\n")
            file.write("#!pragma planner_is_goal_ordered=True\n")
            file.write("#!pragma planner_always_commit_skeleton=True\n\n")
            # Write objects
            file.write("objects:\n")
            file
            for i, obj_type in enumerate(self.item_type):
                if obj_type:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"  {name}:{obj_type}\n")
            file.write("\n#object_end\n\n")
            file.write("#objects\n")
            # Write categories (initial state)
            file.write("init:\n    #categories\n")
            for i, category in enumerate(self.category):
                if category:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"    {category}[{name}]=True\n")
            file.write("    #categories_end\n\n")

            # Write states
            file.write("    #states\n")
            for prop_name, prop_values in self.state.items():
                for i, has_property in enumerate(prop_values):
                    if has_property:
                        if not ("char" in prop_name) and not ("hold" in prop_name):
                            name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                            file.write(f"    {prop_name}[{name}]=True\n")
            file.write("    #states_end\n\n")

            file.write("    #char\n")
            for prop_name, prop_values in self.state.items():
                for i, has_property in enumerate(prop_values):
                    if has_property:
                        if ("char" in prop_name) or ("hold" in prop_name):
                            name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                            file.write(f"    {prop_name}[char,{name}]=True\n")
            file.write("    #char_end\n\n")


            # Write properties
            file.write("    #properties\n")
            for prop_name, prop_values in self.properties.items():
                for i, has_property in enumerate(prop_values):
                    if has_property:
                        name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                        file.write(f"    {prop_name}[{name}]=True\n")
            file.write("    #properties_end\n\n")

            # Write relations
            file.write("    #relations\n")
            for relation_name, relation_matrix in self.relations.items():
                for i, row in enumerate(relation_matrix):
                    for j, has_relation in enumerate(row):
                        if has_relation:
                            name_i = next(name for name, id_ in self.name2opid.items() if id_ == i)
                            name_j = next(name for name, id_ in self.name2opid.items() if id_ == j)
                            file.write(f"    {relation_name}[{name_i},{name_j}]=True\n")
            file.write("    #relations_end\n\n")

            # Write exploration (if necessary)
            file.write("    #exploration\n")
            unknown = self.exploration.get("unknown", [])
            for i, is_unknown in enumerate(unknown):
                if is_unknown:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"    unknown[{name}]=True\n")
            
            checked = self.exploration.get("checked", [])
            for i, row in enumerate(checked):
                for j, is_checked in enumerate(row):
                    if is_checked:
                        name_i = next(name for name, id_ in self.name2opid.items() if id_ == i)


                        name_j = next(name for name, id_ in self.name2opid.items() if id_ == j)

                        file.write(f"    checked[{name_i},{name_j}]=True\n")
            file.write("    #exploration_end\n")

            file.write("\n    #id\n")
            for i, obj_type in enumerate(self.item_type):
                if obj_type:
                    name = next(name for name, id_ in self.name2opid.items() if id_ == i)
                    file.write(f"    id[{name}]={self.name2id[name]}\n")
            file.write("    #id_end\n")

            file.write("\n#goal_representation\n")
            file.write(self.goal_representation)
            file.write("\n#goal_representation_end\n")

    def get_state(self):
        self.save_to_file()
        
        domain = crow.load_domain_file(self.domain_path)
        problem = crow.load_problem_file(self.internal_state_path, domain=domain)
        return problem

    def get_all_info_for_known_items(self,exploration_known):
        known_items_info = {
            "state": {},
            "relations": {},
            "exploration": exploration_known
        }

        known_items = np.where(exploration_known['known'])[0]

        # 获取所有known的物品的states
        for state_name, state_values in self.state.items():
            for item_id in known_items:
                if state_values[item_id] is not None:
                    if state_name not in known_items_info["state"]:
                        known_items_info["state"][state_name] = []
                    known_items_info["state"][state_name].append((item_id, state_values[item_id]))

        # 获取所有known的物品的relations
        for relation_name, relation_matrix in self.relations.items():
            for item_id in known_items:
                for target_id, has_relation in enumerate(relation_matrix[item_id]):
                    if has_relation is not None:
                        if relation_name not in known_items_info["relations"]:
                            known_items_info["relations"][relation_name] = []
                        if self.exploration["known"][target_id]:
                            known_items_info["relations"][relation_name].append((item_id, target_id, has_relation))

        return known_items_info

    def locked(self):
        # 获取所有物品的索引
        item_indices = np.arange(self.num_items + 1)

        # 初始化 locked 状态数组，默认全为 False
        locked_status = np.full(self.num_items + 1, False, dtype=bool)

        # 获取各个条件的布尔数组
        inside_any_container = self.relations['inside']
        closed_containers = self.state.get('closed', np.full(self.num_items + 1, False, dtype=bool))
        eatable_containers = self.properties.get('eatable', np.full(self.num_items + 1, False, dtype=bool))

        # 遍历每个物品，检查其是否满足 locked 的条件
        for obj in item_indices:
            # 条件: inside(obj, container) and closed(container) and not eatable(container)
            is_inside = inside_any_container[obj, :]
            locked_condition = np.logical_and(is_inside, closed_containers)
            locked_condition = np.logical_and(locked_condition, ~eatable_containers)

            # 如果存在任何满足条件的容器，标记该物品为锁定状态
            locked_status[obj] = np.any(locked_condition)

        return locked_status
    
    def inhand(self,obj_category):
        for ob in np.where(self.state['holds_rh'])[0]:
            if self.category[ob]==obj_category:
                return True
        for ob in np.where(self.state['holds_lh'])[0]:
            if self.category[ob]==obj_category:
                return True
        return False

    def step(self,action):
        exploration={}
        Add_obj=False
        Add_obj1_id=None
        Add_obj2_id=None
        if action.name=='walk_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            self.state["close_char"]=np.array([False]*(self.num_items+1))
            self.state["inside_char"]=np.array([False]*(self.num_items+1))
            self.state['close_char'] = self.relations['on'][obj_id]+self.relations['inside'][:,obj_id]+self.relations['close'][obj_id]
            self.state['close_char'][obj_id] = True
            in_lh_obj=np.where(self.state['holds_lh'])[0]
            in_rh_obj=np.where(self.state['holds_rh'])[0]
            if len(in_lh_obj)>0:
                self.state['close_char'][in_lh_obj[0]]=True
            if len(in_rh_obj)>0:
                self.state['close_char'][in_rh_obj[0]]=True
            self.get_state()

        if action.name=='switchoff_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['has_switch'][obj_id]:
                if self.state['is_on'][obj_id]:
                    if self.agent_has_a_free_hand:
                        if self.state['close_char'][obj_id]:
                            self.state['is_on'][obj_id]=False
                            self.state['is_on'][obj_id]=True
                        else:
                            print(f"Agent is far from{obj_name}")
                            raise ValueError
                    else:
                        print(f"Agent does not have a free hand to turn off {obj_name}")
                        raise ValueError
                else:
                    print(f"{obj_name} is already off")
                    raise ValueError
            else:
                print(f"{obj_name} does not have a switch")
                raise ValueError
            
        if action.name=='switchon_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['has_switch'][obj_id]:
                if self.state['is_off'][obj_id]:
                    if self.agent_has_a_free_hand:
                        if self.state['close_char'][obj_id]:
                            self.state['is_off'][obj_id]=False
                            self.state['is_on'][obj_id]=True
                        else:
                            print(f"Agent is far from{obj_name}")
                            raise ValueError
                    else:
                        print(f"Agent does not have a free hand to turn on {obj_name}")
                        raise ValueError
                else:
                    print(f"{obj_name} is already on")
                    raise ValueError
            else:
                print(f"{obj_name} does not have a switch")
                raise ValueError
            
        if action.name=='put_executor':
            ob1=action.arguments[0].name
            ob2=action.arguments[1].name
            ob1_id=self.name2opid[ob1]
            ob2_id=self.name2opid[ob2]
            if self.properties['surfaces'][ob2_id] or self.properties['containers'][ob2_id] or self.properties['can_open'][ob2_id] or self.properties['etable'][ob2_id]:
                if self.state['holds_lh'][ob1_id] or self.state['holds_rh'][ob1_id]:
                    if self.state['close_char'][ob2_id]:
                        
                        self.state['holds_lh'][ob1_id]=False
                        self.state['holds_rh'][ob1_id]=False
                        self.relations['close'][ob1_id]=self.relations['close'][ob2_id]
                        self.relations['close'][ob1_id][ob2_id]=True
                        self.relations['close'][:,ob1_id]=self.relations['close'][:,ob2_id]
                        self.relations['close'][ob2_id][ob1_id]=True
                        inside_obj1=self.relations['inside'][:,ob1_id]
                        if self.properties['surfaces'][ob2_id]:
                            self.relations['on'][ob1_id][ob2_id]=True
                            for ob in np.where(inside_obj1)[0]:
                                self.relations['on'][ob]=self.relations['on'][ob1_id]
                        if self.properties['containers'][ob2_id]:
                            if not self.state['open'][ob2_id] and self.properties['can_open'][ob2_id]:
                                print(f"{ob2} is closed, so cannot put {ob1} in it")
                                raise ValueError
                            self.relations['inside'][ob1_id][ob2_id]=True
                            for ob in np.where(inside_obj1)[0]:
                                self.relations['inside'][ob]=self.relations['inside'][ob1_id]
                                self.relationships['inside'][ob][ob1_id]=True
                        if self.properties['eatable'][ob2_id]:
                            self.relations['inside'][ob1_id][ob2_id]=True
                            self.relations['on'][ob1_id][ob2_id]=True
                            for ob in np.where(inside_obj1)[0]:
                                self.relations['inside'][ob]=self.relations['inside'][ob1_id]
                                self.relations['on'][ob]=self.relations['on'][ob1_id]
                        if self.properties['containers'][ob2_id]:
                            self.state['mixed'][ob2_id]=False
                        Add_obj=True
                        Add_obj1_id=ob1_id
                            
                    else:
                        print(f"Agent is far from {ob2}, so cannot put {ob1} on {ob2}")
                        raise ValueError
                else:
                    print(f"Agent is not holding {ob1}, so cannot put {ob1} on {ob2}")
                    raise ValueError
            else:
                print(f"{ob2} does not have a surface, container, or is not openable or eatable, so you cannot put anything on it")
                raise ValueError
            
        if action.name=='grab_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['grabbable'][obj_id]:
                
                if self.agent_has_a_free_hand:
                    if self.state['close_char'][obj_id]:
                        #####assert pass#####
                        cover_obj=self.relations['inside'][obj_id]
                        for ob in np.where(cover_obj)[0]:
                            if self.state['closed'][ob]:
                                print(f"{obj_name} is locked inside {ob}")
                                raise ValueError
                        grasped=False
                        if not np.any(self.state['holds_lh']):
                            self.state['holds_lh'][obj_id]=True
                            grasped=True
                            if np.any(self.state['holds_rh']):
                                self.agent_has_a_free_hand=False
                        if np.any(self.state['holds_lh']) and not grasped:
                            if np.any(self.state['holds_rh']):
                                print(f"Agent does not have a free hand to grab {obj_name}, and has error when checing has_free_hand")
                                raise ValueError
                            self.state['holds_rh'][obj_id]=True
                            self.agent_has_a_free_hand=False
                            grasped=True
                        self.relations['on'][obj_id]=np.array([False]*(self.num_items+1))
                        self.relations['inside'][obj_id]=np.array([False]*(self.num_items+1))
                        self.relations['close'][obj_id]=np.array([False]*(self.num_items+1))
                        self.relations['on'][:,obj_id]=np.array([False]*(self.num_items+1))
                        self.state['close_char'][obj_id]=True
                else:
                    print(f"Agent does not have a free hand to grab {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} is not grabbable")
                raise ValueError
        
        if action.name=='wash_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            washed=False
            for ob in np.where(self.state['close_char'])[0]:
                if washed:
                    break
                if self.category[ob]=='is_sink':
                    for obb in np.where(self.relations['close'][ob])[0]:
                        if washed:
                            break
                        if self.category[obb]=='is_faucet':
                            if not self.state['is_on'][obb]:
                                print(f"{obb} is off")
                                raise ValueError
                            if not self.relations['inside'][obj_id][ob]:
                                print(f"{obj_name} is not inside {ob}, so {obj_name} can not be washed")
                                raise ValueError
                            ####assert pass####
                            washed=True 
                            self.state['clean'][obj_id]=True
                            self.state['dirty'][obj_id]=False
            if not washed:
                print("failed to wash because the agent is far from the sink or the faucet")
                raise ValueError
                
        if action.name=='open_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['can_open'][obj_id]:
                if self.state['close_char'][obj_id]:
                    if self.agent_has_a_free_hand:
                        self.state['open'][obj_id]=True
                        self.state['closed'][obj_id]=False
                        if self.properties['has_switch'][obj_id] and self.state['is_on'][obj_id]:
                            print(f"open {obj_name} while it is working")#just a warning
                    else:
                        print(f"Agent does not have a free hand to open {obj_name}")
                        raise ValueError
                else:
                    print(f"Agent is far from {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} is not openable")
                raise ValueError


        if action.name=='close_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['can_open'][obj_id]:
                if self.state['open'][obj_id]:
                    if self.agent_has_a_free_hand:
                        self.state['open'][obj_id]=False
                        self.state['closed'][obj_id]=True
                    else:
                        print(f"Agent does not have a free hand to close {obj_name}")
                        raise ValueError
                else:
                    print(f"{obj_name} is already closed")
                    raise ValueError
            else:
                print(f"{obj_name} is not openable")
                raise ValueError
            
        if action.name=='pour_executor':
            obj1=action.arguments[0].name
            obj2=action.arguments[1].name
            obj1_id=self.name2opid[obj1]
            obj2_id=self.name2opid[obj2]
            if self.properties['pourable'][obj1_id]:
                if self.state['holds_lh'][obj1_id] or self.state['holds_rh'][obj1_id]:
                    if self.state['close_char'][obj2_id]:
                        self.relations['inside'][obj_id][obj2_id]=True
                    else:
                        print(f"Agent is far from {obj2}")
                        raise ValueError
                else:
                    print(f"Agent is not holding {obj1}")
                    raise ValueError
            else:
                print(f"{obj1} is not pourable")
                raise ValueError
            
        if action.name=='plugin_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['has_plug'][obj_id]:
                if self.agent_has_a_free_hand:
                    if self.state['close_char'][obj_id]:
                        self.state['unplugged'][obj_id]=False
                        self.state['plugged'][obj_id]=True
                    else:
                        print(f"Agent is far from {obj_name}")
                        raise ValueError
                else:
                    print(f"Agent does not have a free hand to plug {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} does not have a plug")
                raise ValueError
        if action.name=='plugout_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['has_plug'][obj_id]:
                if self.agent_has_a_free_hand:
                    if self.state['close_char'][obj_id]:
                        self.state['plugged'][obj_id]=False
                        self.state['unplugged'][obj_id]=True
                    else:
                        print(f"Agent is far from {obj_name}")
                        raise ValueError
                else:
                    print(f"Agent does not have a free hand to plug {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} does not have a plug")
                raise ValueError
            
        if action.name=='stir_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['containers'][obj_id] or self.properties['eatble'][obj_id]:
                if self.state['close_char'][obj_id]:
                    if self.inhand('is_spatula'):
                        self.state['mixed'][obj_id]=True
                    else:
                        print(f"Agent does not have a spatula")
                        raise ValueError
                else:
                    print(f"Agent is far from {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} is not cookaware")
                raise ValueError
            
        if action.name=='slice_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['cuttable'][obj_id]:
                if self.state['close_char'][obj_id]:
                    if self.inhand('is_knife'):
                        for ob in np.where(self.state['close_char']):
                            if self.category[ob]=='is_cutting_board' and self.relations['on'][obj_id][ob]:
                                self.state['sliced'][obj_id]=True
                                break
                    else:
                        print(f"Agent does not have a knife")
                        raise ValueError
                else:
                    print(f"Agent is far from {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} is not cuttable")
                raise ValueError
            
        if action.name=='peel_executor':
            obj_name=action.arguments[0].name
            obj_id=self.name2opid[obj_name]
            if self.properties['peelable'][obj_id]:
                if self.state['close_char'][obj_id]:
                    if self.category[obj_id] in ['is_potato','is_tomato','is_onion','is_garlic','is_ginger']:
                        if not self.inhand('is_knife'):
                            print(f"Agent does not have a knife")
                            raise ValueError
                    self.state['peeled'][obj_id]=True
                else:
                    print(f"Agent is far from {obj_name}")
                    raise ValueError
            else:
                print(f"{obj_name} is not peelable")
                raise ValueError
            
        exploration['known'] = np.logical_and(self.state['close_char'],np.logical_not(self.locked()))
        if Add_obj:
            exploration['known'][Add_obj1_id]=True
            if Add_obj2_id:
                exploration['known'][Add_obj2_id]=True
        checked=np.full((self.num_items+1,self.num_items+1),False,dtype=bool)
        for ob in np.where(exploration['known'])[0]:
            for obb in np.where(~exploration['known'])[0]:
                checked[obb][ob]=True
        self.exploration['known'] += exploration['known']
        exploration['checked'] = checked
        known_info=self.get_all_info_for_known_items(exploration)
        return known_info





# env = KitchenEnvironment("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/combined_generated.cdl")
# print(env)
# env.save_to_file()
# agent = Agent("combined_generated.cdl")
# print(agent)
