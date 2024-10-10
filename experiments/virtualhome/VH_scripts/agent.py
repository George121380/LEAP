import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/utils')
import concepts.dm.crow as crow
import numpy as np
import re
from library import behavior_library
from experiments.virtualhome.VH_scripts.planning import VH_pipeline
from Interpretation import exploration_VH,sub_goal_generater,obs_query,sub_goal_evaluate
from action_explaination import controller_to_natural_language
import pdb

class VHAgent:
    def __init__(self, filepath,logger,PO=True):
        # Initialize dictionaries

        self.logger=logger

        self.name2opid = {}
        self.name2id = {}
        self.num_items = 0 # Record how mani items in the scene
        self.item_type = np.array([], dtype=object) # Record the type of each item
        self.category = {}
        self.properties = {}
        self.relations = {}
        self.state = {}
        self.character_state = {}
        self.exploration = {}
        self.download_mode='ALL' # how to download behaviors from library
        # Task information
        self.task_name=''
        self.goal_nl=''
        self.current_subgoal_nl=''
        self.current_subgoal_num=0
        self.self_evaluate_num=0
        self.current_sub_task_guided=False
        self.sub_goal_list=[]
        self.add_info_nl=''
        self.add_info_human_instruction=''
        self.add_info_trial_and_error_info=''
        self.current_subtask_guidance=''
        self.add_info_action_history=[]
        self.exploration_behavior = ""
        self.goal_representation = ""
        self.behaviors_from_library={} # all skills in library
        self.behaviors_from_library_representation='' # used skills' representation
        """
        path to the CDL files
        internal_executable_file_path: the file can be solve py planner: state + goal
        basic_domain_knowledge_file_path: domain knowledge
        state_file_path: the file contains the current state: state (only)        
        """
        if PO:
            self.internal_executable_file_path = 'experiments/virtualhome/CDLs/internal_executable.cdl'
        else:
            self.internal_executable_file_path = 'experiments/virtualhome/CDLs/internal_executable_NPO.cdl'
        self.basic_domain_knowledge_file_path = 'experiments/virtualhome/CDLs/virtualhome_partial.cdl'
        self.state_file_path = 'experiments/virtualhome/CDLs/current_agent_state.cdl'
        self.reset_add_info_record()
        self.reset_goal_representation_record()
        # do not replan every step
        self.newfind=True
        self.plan=[]
        self.current_step=0
        self.exp_fail_num=0
        self.error_times=0
        self.max_replan_num=3
        self.library=behavior_library()
        self._parse_file(filepath)
        self.save_to_file()
        self.save_to_file(self.state_file_path)

    def lift_behaviors(self):
        # add executable behaviors to the library
        self.library.lift_group(self.task_name,self.current_subgoal_nl,self.goal_representation)

    def download_behaviors_from_library(self):
        # download behaviors from the library
        self.behaviors_from_library['content'],self.behaviors_from_library['names'],self.behaviors_from_library['function_calls'],self.behaviors_from_library['behavior_calls']=self.library.download_behaviors(self.task_name,self.current_subgoal_nl,self.download_mode)
        return self.behaviors_from_library

    def reset_visited(self):
        # reset the visited state
        self.state['visited']=np.full(self.num_items , "uncertain", dtype=object)

    def set_human_helper(self,human_helper):
        self.human_helper=human_helper
        self.human_helper.set_name2id(self.name2id)

    def query_human(self,question:str):
        record='Record from func query_human in agent.py\n'
        record+=f'Question: {question}\n'
        answer=self.human_helper.QA(question)
        record+=f'Answer: {answer}\n'
        self.logger.info("","","","",record,"")
        return answer
    
    def ask_for_human_task_guidance(self):
        self.current_sub_task_guided=True
        question=f'Can you teach me how to "{self.current_subgoal_nl.lower()}" ?'
        Human_Guidance=self.query_human(question)
        self.current_subtask_guidance=Human_Guidance
        self.update_add_info()

        self.record_add_info()
        self.error_times=0
    
    def set_initial_human_instruction(self,goal):
        # debug used
        self.goal_nl=goal
        ini_human_instruction=self.query_human(f"Can you tell me how to {self.goal_nl.lower()}")
        if ini_human_instruction!="I don't know.":
            self.add_info_human_instruction=f"To {self.goal_nl.replace('.',',').lower()} you can {ini_human_instruction.lower()}"
        self.update_add_info()
        

    def update_add_info(self):
        self.add_info_nl=''
        if self.add_info_human_instruction:
            self.add_info_nl+=f"Human Instruction: {self.add_info_human_instruction}\n"

        if self.current_subtask_guidance:
            self.add_info_nl+=f"Human Guidance: {self.current_subtask_guidance}\n"

        if self.add_info_trial_and_error_info:
            self.add_info_nl+=f"Trial and Error: {self.add_info_trial_and_error_info}\n"

        if self.add_info_action_history:
            self.add_info_nl+="The actions you have taken:\n"
            for id in range(len(self.add_info_action_history)):
                self.add_info_nl+=f"Action {id+1}: {controller_to_natural_language(self.add_info_action_history[id]['action'])} -> effect: {self.add_info_action_history[id]['effects']}\n"

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
            "clean", "plugged", "unplugged", "facing_char","on_char", "on_body","close_char", "inside_char","holds_rh", "holds_lh",'has_water','cut','visited'
        ]
        for feature in state_features:
            self.state[feature] = np.full(self.num_items , "uncertain", dtype=object)

    def _initialize_character_states(self):
        self.character_state['standing']=True
        self.character_state['sitting']=False
        self.character_state['lying']=False
        self.character_state['sleeping']=False

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

        behavior_from_library = re.search(r'#behaviors_from_library\n(.+?)#behaviors_from_library_end', content, re.DOTALL)
        if behavior_from_library:
            behavior_from_library = behavior_from_library.group(1)
            self.behaviors_from_library_representation = behavior_from_library

        # Read goal representation
        goal_rep=re.search(r'#goal_representation\n(.+?)#goal_representation_end', content, re.DOTALL)
        if goal_rep:
            goal_representation_section = goal_rep.group(1)
            self.goal_representation = goal_representation_section
        # if not goal_rep:
        #     print("No goal representation yet")
        # Set uncertain information for unknown items
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
            path = self.internal_executable_file_path

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

            if path == self.internal_executable_file_path:
                file.write("\n#exp_behavior\n")
                file.write(self.exploration_behavior)
                file.write("\n#exp_behavior_end\n")
                file.write("\n#behaviors_from_library\n")
                file.write(self.behaviors_from_library_representation)
                file.write("\n#behaviors_from_library_end\n")
                file.write("\n#goal_representation\n")
                file.write(self.goal_representation)
                file.write("\n#goal_representation_end\n")
    
    def updates(self,observation):
        if "You can not" in observation: # if this action is not executable
            self.add_info_trial_and_error_info+=observation
            self.update_add_info()
            self.record_add_info()
            self.reset_sub_goal()

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
                        self.update_add_info()
                        self.logger.info("","","",self.add_info_nl,"","")
                        self.record_add_info()

                    self.exp_fail_num+=1
                    print(f'{exp_target} is not around {exp_loc}, re-explore')
                    action_effects+=f"Failed to find {exp_target} around {exp_loc}. "
                    self.save_to_file()
                    self.save_to_file(self.state_file_path)
                    self.exploration_behavior=exploration_VH(self.goal_nl,self.add_info_nl,self.internal_executable_file_path,self.exploration['checked'])
                    self.newfind=True

            if observation['obs_flag']:
                obs_target=observation['obs_target']
                self.state['visited'][self.name2opid[obs_target]]=True
                for new_known in observation['known']:
                    if 'character' in new_known:
                        continue
                    if self.exploration['unknown'][self.name2opid[new_known]]==True:
                        self.exploration['unknown'][self.name2opid[new_known]]=False
                        self.newfind=True # find sth new
                
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
            
            self.annotation(observation)

            self.add_info_action_history.append({'action':str(observation['action']),'effects':action_effects})
            self.update_add_info()
            self.logger.info("","",str(observation['action']),action_effects,"","")
            self.record_add_info()
            self.save_to_file()
            self.save_to_file(self.state_file_path)   

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



    def organize_obs_result(self,observation):
        discription=''
        for info in observation:
            if 'from_name' in info:
                from_name=info['from_name']
                to_name=info['to_name']
                r=info['relation_type']
                if r=='CLOSE':
                    discription+=f' {from_name} is close to {to_name}.'
                elif r=='FACING':
                    discription+=f' {from_name} is facing {to_name}.'
                elif r=='INSIDE':
                    discription+=f' {from_name} is inside {to_name}.'
                elif r=='ON':
                    discription+=f' {from_name} is on {to_name}.'
                elif r=='BETWEEN':
                    discription+=f' {from_name} is between {to_name}.'
            if 'states' in info:
                discription+=info['states']
        return discription

    def obs_query(self,target_obj:str,observation,question=None):
        # target_obj: the name of the object that the observation is about
        discription=self.organize_obs_result(observation)
        obs_info=obs_query(target_obj,discription,question)
        return obs_info

    def get_state(self):
        # Get the current CDL state of the agent, "problem" will be used by CDL Solver
        domain = crow.load_domain_file(self.basic_domain_knowledge_file_path)
        problem = crow.load_problem_file(self.internal_executable_file_path, domain=domain)
        return problem

    def act(self):
        while self.error_times<self.max_replan_num:
            if self.newfind:
                # pdb.set_trace()
                cdl_state = self.get_state()
                plans, stats = crow.crow_regression(
                cdl_state.domain, cdl_state, goal=cdl_state.goal, min_search_depth=12, max_search_depth=12,
                is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True,
                enable_state_hash=False,
                verbose=False
            )
                if len(plans) == 0:
                    self.error_times+=1
                    if self.current_subgoal_num==0:
                        print('No plan found. Reset the whole goal')
                        self.reset_goal(self.goal_nl,self.classes,self.task_name,First_time=False,sub_goal=True)
                    else:
                        print('No plan found. Reset the sub-goal')
                        self.reset_sub_goal()
                    continue

                plan = plans[0]
                if len(plan) == 0:# This can also be a situation that this sub-task is already finished before.
                    self.error_times+=1
                    print('plan is a empty list')
                    if self.current_subgoal_num==0:
                            print('No plan found. Reset the whole goal')
                            self.reset_goal(self.goal_nl,self.classes,self.task_name,First_time=False,sub_goal=True)
                    else:
                        print('No plan found. Reset the sub-goal')
                        self.reset_sub_goal()
                    continue
                
                # When the plan is found, we need to lift the behaviors to the library
                print('Plan found')
                plan_print=''
                for action in plan:
                    plan_print+=(str(action))
                print(plan_print)
                self.logger.info("","","","","",str(plan))
                action = plan[0]
                self.current_step=1
                self.plan=plan
                self.newfind=False
                return action,plan #reset
            
            else:
                if self.current_step==len(self.plan):
                    print('This is the last step for current sub-task')
                    ########## evaluate subgoal start ###########
                    while True:
                        result,insrtuctions=self.evaluate_current_subgoal()
                        self.self_evaluate_num+=1
                        
                        if result.lower()=='yes':
                            #move to next subgoal
                            self.self_evaluate_num=0
                            print('Sub-task is done')
                            self.lift_behaviors()
                            self.current_subgoal_num+=1
                            self.current_sub_task_guided=False # reset the guided flag
                            self.current_subtask_guidance=''
                            break
                            
                        if self.self_evaluate_num==3:
                            self.self_evaluate_num=0
                            print('Try to evaluate the sub-task for 3 times, but still failed. Force to move to the next sub task')
                            result='yes'
                            self.current_subgoal_num+=1
                            self.current_sub_task_guided=False # reset the guided flag
                            self.current_subtask_guidance=''
                            break

                        if result.lower()=='no':
                            # regenerate the subgoal
                            self.add_info_human_instruction=insrtuctions+'\n'
                            self.update_add_info()
                            self.logger.info("","","",self.add_info_nl,"","")
                            self.reset_sub_goal()
                            self.newfind=True
                            self.record_add_info()
                            break
                        
                        if result.lower()!='yes' and result.lower()!='no':
                            print('Evaluate error, try again')

                    if result.lower()=='no':
                        continue

                    ########## evaluate subgoal end ###########
                    if self.current_subgoal_num==len(self.sub_goal_list):
                        print('All sub-tasks are done')
                        return "over",None
                    
                    else: # generate goal representation for next sub-task
                        self.current_subgoal_nl=self.sub_goal_list[self.current_subgoal_num]
                        self.reset_sub_goal()
                        continue

                action=self.plan[self.current_step]
                self.current_step+=1
                return action,self.plan
        # Beyond the max replan number
        if not self.current_sub_task_guided: # if not guided by human
            self.ask_for_human_task_guidance()
            self.reset_sub_goal()
            return "human guided",None
        else:
            return "Failed",None

    def reset_goal(self,goal,classes,task_name,First_time=False,sub_goal=True):
        """
        Args:
            goal: Full goal of the whole task
            additional_information: Human instruction + Human guidance + Action history
            classes: the classes of the objects in the environment
            First_time: whether it is the first time to set the goal
            sub_goal: whether we want to split the goal into sub-goals
        """
        self.newfind=True
        if First_time:
            self.goal_nl=goal
            self.task_name=task_name
            self.record_add_info()
            self.classes=classes

        self.sub_goal_list=sub_goal_generater(goal)
        print(self.sub_goal_list)
        record='Reset goals: The sub-goals are: \n'+str(self.sub_goal_list)
        self.logger.info(record,"","","","","")
        self.current_subgoal_nl=self.sub_goal_list[0]
        # pdb.set_trace()
        _,self.goal_representation,self.exploration_behavior,self.behaviors_from_library_representation=VH_pipeline(self.state_file_path,self.internal_executable_file_path,self.current_subgoal_nl,self.add_info_nl,self.goal_nl,self.sub_goal_list[:self.current_subgoal_num],self.classes,self.behaviors_from_library)
        # pdb.set_trace()
        self.logger.info(self.goal_representation,"From function reset_goal","","","","")

        if self.goal_representation==None:
            if self.current_sub_task_guided:
                print("Failed to generate the goal representation after asking for human guidance")
                return
            else: # Try again after asking for human guidance
                self.ask_for_human_task_guidance()
                _,self.goal_representation,self.exploration_behavior,self.behaviors_from_library_representation=VH_pipeline(self.state_file_path,self.internal_executable_file_path,self.current_subgoal_nl,self.add_info_nl,self.goal_nl,self.sub_goal_list[:self.current_subgoal_num],self.classes,self.behaviors_from_library)
                if self.goal_representation==None:
                    print("Failed to generate the goal representation after asking for human guidance")
                    return

    def reset_sub_goal(self):
        self.newfind=True
        _,self.goal_representation,self.exploration_behavior,self.behaviors_from_library_representation=VH_pipeline(self.state_file_path,self.internal_executable_file_path,self.current_subgoal_nl,self.add_info_nl,self.goal_nl,self.sub_goal_list[:self.current_subgoal_num],self.classes,self.behaviors_from_library)
        if self.goal_representation==None:
            if self.current_sub_task_guided:
                print("Failed to generate the goal representation after asking for human guidance")
                return
            else: # Try again after asking for human guidance
                self.ask_for_human_task_guidance()
                _,self.goal_representation,self.exploration_behavior,self.behaviors_from_library_representation=VH_pipeline(self.state_file_path,self.internal_executable_file_path,self.current_subgoal_nl,self.add_info_nl,self.goal_nl,self.sub_goal_list[:self.current_subgoal_num],self.classes,self.behaviors_from_library)
                if self.goal_representation==None:
                    print("Failed to generate the goal representation after asking for human guidance")
                    return
        self.logger.info(self.goal_representation,"From function reset_sub_goal","","","","")
        self.reset_visited()
        self.record_goal_representation()
        self.save_to_file()
        self.save_to_file(self.state_file_path)
        

    def evaluate_current_subgoal(self):
        if self.current_subgoal_num==len(self.sub_goal_list)-1:
            result,insrtuctions=sub_goal_evaluate(self.goal_representation,self.add_info_action_history,self.current_subgoal_nl,self.goal_nl, 'This is the last sub-task',self.add_info_nl,self.name2opid.keys())
        else:
            result,insrtuctions=sub_goal_evaluate(self.goal_representation,self.add_info_action_history,self.current_subgoal_nl,self.goal_nl, self.sub_goal_list[self.current_subgoal_num+1],self.add_info_nl,self.name2opid.keys())
        return result,insrtuctions
    
    def reset_add_info_record(self):
        record_path='visualization/add_info_monitor.txt'
        with open(record_path,'w') as f:
            f.write('')

    def record_add_info(self):
        record_path='visualization/add_info_monitor.txt'
        with open(record_path,'w') as f:
            f.write(self.add_info_nl)

    def reset_goal_representation_record(self):
        record_path='visualization/goal_representation_monitor.txt'
        with open(record_path,'w') as f:
            f.write('')
    
    def record_goal_representation(self):
        record_path='visualization/goal_representation_monitor.txt'
        with open(record_path,'w') as f:
            f.write(self.goal_representation)