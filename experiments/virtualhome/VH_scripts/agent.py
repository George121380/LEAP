import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/utils')
import concepts.dm.crow as crow
import numpy as np
import re
from experiments.virtualhome.VH_scripts.planning import VH_pipeline
from Interpretation import exploration_VH

class VHAgent:
    def __init__(self, filepath):
        self.name2opid = {}
        self.name2id = {}
        self.num_items = 0
        self.item_type = np.array([], dtype=object)
        self.category = {}
        self.properties = {}
        self.relations = {}
        self.state = {}
        self.exploration = {}
        self.goal_nl=''
        self.add_info_nl=''
        self.exploration_behavior = ""
        self.goal_representation = ""
        self.internal_state_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/virtualhome_agent_internal_state.cdl'
        self.domain_path = '/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/virtualhome_partial.cdl'

        # do not replan every step
        self.newfind=True
        self.plan=[]
        self.current_step=0

        self._parse_file(filepath)
        self.save_to_file()

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
            "clean", "plugged", "unplugged", "facing_char","on_char", "on_body","close_char", "inside_char","holds_rh", "holds_lh"
        ]
        for feature in state_features:
            self.state[feature] = np.full(self.num_items , "uncertain", dtype=object)

    def _initialize_properties(self):
        property_features = [
            "surfaces", "grabbable", "sittable","lieable","hangable","drinkable","eatable","recipient","cuttable", "pourable", 
            "can_open", "has_switch", "containers", "has_plug", "readable","lookable","clothes","person","body_part","cover_object","has_paper","movable","cream"
        ]
        for feature in property_features:
            self.properties[feature] = np.full(self.num_items , "uncertain", dtype=object)

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
                if not value in self.category:
                    self.category[value]=set()
                self.category[value].add(key)

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
                    new_state = np.full(self.num_items , False, dtype=bool)
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
                    new_state = np.full(self.num_items , False, dtype=bool)
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
                    new_properties = np.full(self.num_items , False, dtype=bool)
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
        for obj_id in range(1, self.num_items ):
            if not self.exploration["unknown"][obj_id]:
                # For objects that are not known, set properties and relations to "uncertain"
                # for prop_name in self.properties:
                #     self.properties[prop_name][obj_id] = "uncertain"
                for relation_name in self.relations:
                    for i in range(self.num_items ):
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
                    for i in range(self.num_items ):
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
            for item in self.category:
                for cat in self.category[item]:
                    file.write(f"    {cat}[{item}]=True\n")
            # for i, category in enumerate(self.category):
            #     if category:
            #         name = next(name for name, id_ in self.name2opid.items() if id_ == i)
            #         file.write(f"    {category}[{name}]=True\n")
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
            
            # checked = self.exploration.get("checked", [])
            # for i, row in enumerate(checked):
            #     for j, is_checked in enumerate(row):
            #         if is_checked and is_checked != "uncertain":
            #             if i==0 or j==0:
            #                 continue
            #             name_i = next(name for name, id_ in self.name2opid.items() if id_ == i)
            #             name_j = next(name for name, id_ in self.name2opid.items() if id_ == j)
            #             file.write(f"    checked[{name_i},{name_j}]=True\n")
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

    def updates_from_diy_env(self,observation):
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
    
    def updates(self,observation):
        # print(observation['known'])
        if not observation['exp_flag']:# other actions
            for new_known in observation['known']:
                if 'character' in new_known:
                    continue
                if self.exploration['unknown'][self.name2opid[new_known]]==True:
                    self.exploration['unknown'][self.name2opid[new_known]]=False
            
            for check_place in observation['checked']:
                if 'character' in check_place:
                    continue
                self.exploration['checked'][:,self.name2opid[check_place]]=True

            for new_relations in observation['relations']:
                if 'character' in new_relations['to_name']:
                    new_relations['to_name']='char'
                if new_relations['from_name']=='char':
                    
                    if new_relations['relation_type']=='HOLDS_LH':
                        self.state['holds_lh'][self.name2opid[new_relations['to_name']]]=True
                    elif new_relations['relation_type']=='HOLDS_RH':
                        self.state['holds_rh'][self.name2opid[new_relations['to_name']]]=True
                    else:
                        relation_type=new_relations['relation_type'].lower()+"_char"
                        self.state[relation_type][self.name2opid[new_relations['to_name']]]=True
                elif new_relations['to_name']=='char' and new_relations['relation_type']=='ON':
                    self.state['on_body'][self.name2opid[new_relations['from_name']]]=True
                else:
                    self.relations[new_relations['relation_type'].lower()][self.name2opid[new_relations['from_name']]][self.name2opid[new_relations['to_name']]]=True
            
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

            

        else:# exploration
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
            else:
                print(f'{exp_target} is not around {exp_loc}, re-explore')
                self.save_to_file()
                self.exploration_behavior=exploration_VH(self.goal_nl,self.add_info_nl,self.internal_state_path,self.exploration['checked'])
                self.newfind=True

        self.save_to_file()
        self.save_to_file("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/current_agent_state.cdl")   


    def get_state(self):

        domain = crow.load_domain_file(self.domain_path)
        problem = crow.load_problem_file(self.internal_state_path, domain=domain)
        return problem

    def act(self):
        if self.newfind:
            cdl_state = self.get_state()
            plans, stats = crow.crow_regression(
            cdl_state.domain, cdl_state, goal=cdl_state.goal, min_search_depth=8, max_search_depth=8,
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
            self.current_step=1
            self.plan=plan
            self.newfind=False
            return action,plan

        else:
            if self.current_step==len(self.plan):
                print('This is the last step')
                raise ValueError('This is the last step')
            action=self.plan[self.current_step]
            self.current_step+=1
            return action,self.plan

    def reset_goal(self,goal,additional_information,classes,First_time=False):
        # self.goal_representation=pipeline(goal,additional_information,loop=False,First_time=First_time)
        self.goal_nl=goal
        self.add_info_nl=additional_information
        _,self.goal_representation,self.exploration_behavior=VH_pipeline(goal,additional_information,classes)
        self.save_to_file()
        self.save_to_file("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/current_agent_state.cdl")
