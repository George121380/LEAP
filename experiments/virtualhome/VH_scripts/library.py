import json
import sys
import re
sys.path.append('prompt')
from ask_GPT import ask_GPT
import os

class behavior_library:
    def __init__(self,epoch_path):
        # self.source_path='experiments/virtualhome/resources/library_data.json'
        self.source_path=os.path.join(epoch_path,'library_data.json')
        if not os.path.exists(self.source_path):
            os.makedirs(os.path.dirname(self.source_path), exist_ok=True)
            with open(self.source_path, "w") as f:
                json.dump({}, f)
        metadata = json.load(open(self.source_path, "r"))
        if len(metadata)==0:
            self.behavior_data = {}
            self.function_name_mapping = {}
            self.function_name_counts = {}
        else:
            self.behavior_data= metadata['behavior_data']
            self.function_name_mapping = metadata['function_name_mapping'] # record the mapping relationship of function names
            self.function_name_counts = metadata['function_name_counts'] # record the count of function names for generating suffix
        self.behavior_name_set=set()
        # self.visualization_path='experiments/virtualhome/resources/library_visualization.txt'
        self.visualization_path=os.path.join(epoch_path,'library_visualization.txt')


    def extract_behavior_name(self,behavior:str):
        """
        Args:
            behavior: A behavior definition
        Returns:
            behavior_name: The name of the behavior
        """
        pattern = re.compile(r'(\w+)\s*\(.*?\)')
        behavior_name = pattern.findall(behavior)
        if behavior_name:
            behavior_name = behavior_name[0]
        else:
            raise ValueError("Parsing invalid behavior")
        return behavior_name
    
    def extract_function_name(self,function_def):
        """
        Args:
            function_def: A function definition
        Returns:
            function_name: The name of the function
        """
        pattern = r'^def\s+(\w+)\s*\('
        match = re.match(pattern, function_def.strip())
        if match:
            return match.group(1)
        else:
            return None

    def replace_function_calls(self, code): # replace function calls in the code to avoid conflicts
        pattern = r'\b(\w+)\s*\('

        def replace_match(match):
            func_name = match.group(1)
            new_func_name = self.function_name_mapping.get(func_name, func_name)
            return new_func_name + '('

        lines = code.split('\n')
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('def ') or stripped_line.startswith('behavior '):
                new_lines.append(line)
            else:
                new_line = re.sub(pattern, replace_match, line)
                new_lines.append(new_line)
        return '\n'.join(new_lines)
        
    def extract_behavior_function_calls(self, function_list, behavior_list):
        """
        Args:
            function_list: A list of function definitions
            behavior_list: A list of behavior definitions
        Returns:
            behavior_function_calls: A dictionary mapping behavior names to the functions they call (full function definitions)
        """
        # Extract all function names and create a mapping from function names to their definitions
        function_definitions = {}
        function_names = set()
        pattern = r'^def\s+(\w+)\s*\('
        for function_def in function_list:
            match = re.match(pattern, function_def.strip())
            if match:
                func_name = match.group(1)
                function_names.add(func_name)
                function_definitions[func_name] = function_def

        # Handle the case when function_names is empty
        if not function_names:
            function_call_pattern = None
        else:
            # Build a regex pattern to match function calls
            function_call_pattern = re.compile(r'\b(' + '|'.join(function_names) + r')\s*\(')

        behavior_function_calls = {}
        for behavior_def in behavior_list:
            # Extract behavior name
            behavior_match = re.match(r'^behavior\s+(\w+)\s*\(', behavior_def.strip())
            if behavior_match:
                behavior_name = behavior_match.group(1)
            else:
                continue
            body_start = behavior_def.find('body:')
            if body_start == -1:
                continue
            body = behavior_def[body_start + len('body:'):]

            called_functions = set()
            if function_call_pattern:
                # Search for function calls in the behavior body
                for line in body.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    matches = function_call_pattern.findall(line)
                    for match in matches:
                        called_functions.add(match)
            else:
                # If no functions are defined, no function calls can be detected
                pass

            # Retrieve the full function definitions for the called functions
            called_function_defs = []
            for func_name in called_functions:
                func_def = function_definitions.get(func_name)
                if func_def:
                    called_function_defs.append(func_def)

            behavior_function_calls[behavior_name] = called_function_defs

        return behavior_function_calls

    def remove_conflicts(self, functions, behaviors):
        """
        Function name may repeat.
        Args:
            functions: A list of function definitions
            behaviors: A list of behavior definitions
        Returns:
            function_list: A list of function definitions without conflicts
            behavior_list: A list of behavior definitions without conflicts 
        """
        function_list=[]
        behavior_list=[]
        for function_def in functions:
            function_name = self.extract_function_name(function_def)
            if function_name is None:
                continue

            count = self.function_name_counts.get(function_name, 1)
            new_function_name = f"{function_name}_{count}"
            self.function_name_counts[function_name] = count + 1
            function_def = function_def.replace(f'def {function_name}(', f'def {new_function_name}(')
            function_def = self.replace_function_calls(function_def)
            self.function_name_mapping[function_name] = new_function_name
            function_list.append(function_def)

        for behavior_def in behaviors:
            behavior_def = self.replace_function_calls(behavior_def)
            behavior_list.append(behavior_def)

        return function_list, behavior_list

    def init_behavior_name_set(self):
        for key in self.behavior_data.keys():
            for behavior in self.behavior_data[key]:
                self.behavior_name_set.add(self.extract_behavior_name(behavior['cdl']))

    def save_library(self):
        data_to_save = {
            'behavior_data': self.behavior_data,
            'function_name_mapping': self.function_name_mapping,
            'function_name_counts': self.function_name_counts
        }
        
        with open(self.source_path, "w") as file:
            json.dump(data_to_save, file, indent=4)
        
        with open(self.visualization_path, 'w', encoding='utf-8') as txt_file:
            for category, behaviors in self.behavior_data.items():
                txt_file.write(f"{category}:\n")
                for behavior in behaviors:
                    txt_file.write(behavior['cdl'].replace("\\n", "\n"))
                    txt_file.write("\n\n")

    
    def parse_goal_representation(self,goal_representation:str):
        """
        Args:
            goal_representation: A group of behaviors

        Returns:
            definitions: A list of functions
            behaviors: A list of behavior definitions
        """
        definitions = []
        behaviors = []
        current_block = []
        current_type = None
        for line in goal_representation.splitlines():
            stripped_line = line.strip()

            # Detect the start of a new function definition
            if stripped_line.startswith("def"):
                if current_block:
                    if current_type == "def":
                        definitions.append("\n".join(current_block))
                    elif current_type == "behavior":
                        behaviors.append("\n".join(current_block))
                current_block = [line]
                current_type = "def"
            # Detect the start of a new behavior definition
            elif stripped_line.startswith("behavior"):
                if current_block:
                    if current_type == "def":
                        definitions.append("\n".join(current_block))
                    elif current_type == "behavior":
                        behaviors.append("\n".join(current_block))
                current_block = [line]
                current_type = "behavior"
            else:
                current_block.append(line)

        # Add the last block of code
        if current_block:
            if current_type == "def":
                definitions.append("\n".join(current_block))
            elif current_type == "behavior":
                behaviors.append("\n".join(current_block))

        return definitions, behaviors

    def lift(self, task_name: str, source_sub_task: str, behavior_description: str, behavior_cdl: str, called_function_defs: list):
        """
        Args:
            task_name: The task name that the behavior is associated with
            source_sub_task: where the behavior is created
            behavior_description: the description of the behavior
            behavior_cdl: cdl representation for this behavior
            called_function_defs: A list of function definitions
        """
        behavior_name = self.extract_behavior_name(behavior_cdl)
        if behavior_name in self.behavior_name_set:
            return
        else:
            self.behavior_name_set.add(behavior_name)            
            behavior_info = {
                'usage_description': behavior_description,
                'cdl': behavior_cdl,
                'source_sub_task': source_sub_task,
                'functions': called_function_defs
            }
            
            if task_name in self.behavior_data:
                self.behavior_data[task_name].append(behavior_info)
            else:
                self.behavior_data[task_name] = [behavior_info]
            self.save_library()

    # def download_behaviors(self,task_name:str,current_subgoal_nl:str,download_mode:str):
    #     """
    #     Args:
    #         task_name: The task name that the behavior is associated with
    #         current_subgoal_nl: the description of the current subgoal
    #         download_mode: the mode of downloading
    #     """
    #     if download_mode=='ALL': # Let LLM Choose related behaviors from the whole library
    #         all_behaviors=[]
    #         behavior_names=[]
    #         function_calls=[]
    #         for key in self.behavior_data.keys():
    #             for behavior in self.behavior_data[key]:
    #                 all_behaviors.append(behavior['cdl'])
    #                 behavior_name=(behavior['cdl'].split('\n')[0].replace('behavior ', '', 1))
    #                 behavior_names.append(behavior_name)
    #                 function_calls.append({'behavior_name':behavior_name,'function_calls':behavior['functions']})
        
    #     return all_behaviors,behavior_names,function_calls

    def download_behaviors(self, task_name: str, current_subgoal_nl: str, download_mode: str):
        """
        Args:
            task_name: The task name that the behavior is associated with
            current_subgoal_nl: the description of the current subgoal
            download_mode: the mode of downloading
        Returns:
            all_behaviors: List of behavior CDL strings
            behavior_names: List of behavior names
            function_calls: List of dictionaries with behavior names and their called functions
            behavior_calls: List of dictionaries with behavior names and the behaviors they call
        """
        if download_mode == 'ALL':  # Let LLM Choose related behaviors from the whole library
            all_behaviors = []
            behavior_names = []
            function_calls = []
            behavior_calls = []

            all_behavior_names = set()
            for key in self.behavior_data.keys():
                for behavior in self.behavior_data[key]:
                    behavior_name = self.extract_behavior_name(behavior['cdl'])
                    if behavior_name:
                        all_behavior_names.add(behavior_name)

            behavior_call_pattern = re.compile(r'\b(' + '|'.join(all_behavior_names) + r')\s*\(')

            for key in self.behavior_data.keys():
                for behavior in self.behavior_data[key]:
                    behavior_cdl = behavior['cdl']
                    all_behaviors.append(behavior_cdl)

                    behavior_name = self.extract_behavior_name(behavior_cdl)
                    behavior_names.append(behavior_name)

                    function_calls.append({
                        'behavior_name': behavior_name,
                        'function_calls': behavior['functions']
                    })

                    called_behaviors = self.extract_behavior_calls(behavior_cdl, behavior_name, behavior_call_pattern)
                    behavior_calls.append({
                        'behavior_name': behavior_name,
                        'behavior_calls': called_behaviors
                    })

        return all_behaviors, behavior_names, function_calls, behavior_calls

    def extract_behavior_calls(self, behavior_cdl, current_behavior_name, behavior_call_pattern):
        """
        Extracts the behaviors called by a given behavior.

        Args:
            behavior_cdl: The CDL string of the behavior
            current_behavior_name: The name of the current behavior
            behavior_call_pattern: Compiled regex pattern to match behavior calls

        Returns:
            called_behaviors: A list of behavior names that the current behavior calls
        """
        body_start = behavior_cdl.find('body:')
        if body_start == -1:
            return []

        body = behavior_cdl[body_start + len('body:'):]

        called_behaviors = set()
        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            matches = behavior_call_pattern.findall(line)
            for match in matches:
                if match != current_behavior_name:
                    called_behaviors.add(match)

        return list(called_behaviors)

    def lift_group(self,task_name:str,source_sub_task:str,goal_representation:str):
        """
        Args:
            task_name: The task name that the behavior is associated with
            source_sub_task: where the behavior is created
            goal_representation: A group of behaviors
        """
        definitions, behaviors = self.parse_goal_representation(goal_representation)
        definitions_list, behaviors_list = self.remove_conflicts(definitions, behaviors)
        # behavior_function_calls = self.extract_behavior_function_calls(definitions_list, behaviors_list)

        for behavior in behaviors_list:
            if not '__goal__'in behavior:
                behavior_description = ''
                self.lift(task_name,source_sub_task,behavior_description,behavior,definitions_list)

    def delete(self,task_name,behavior_description):
        """
        Args:
            task_name: The task name that the behavior is associated with
            behavior_description: the description of the behavior
        """
        for i in range(len(self.behavior_data[task_name])):
            if self.behavior_data[task_name][i]['usage_description']==behavior_description:
                self.behavior_data[task_name].pop(i)
                break
        
        self.save_library()
        

if __name__ == "__main__":
    library=behavior_library()
    new_rep="""

behavior transfer_to_bowl_and_cool123(vegetables:item, bowl:item, stove:item):
    body:
        achieve inside(vegetables, bowl)
        achieve is_off(stove)

behavior __goal__():
    body:
        transfer_to_bowl_and_cool(vegetables, bowl, stove)
        close_fridge(fridge)
        move_char_to_chicken(chicken)
"""

    # library.lift_group('123','13',rep)
    behavior_from_library={}
    behavior_from_library['content'],behavior_from_library['names'],behavior_from_library['function_calls'],behavior_from_library['behavior_calls']=library.download_behaviors('123','13','ALL')
    add_info=find_behavior_from_library(new_rep,behavior_from_library)
    print(add_info)
