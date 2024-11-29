import json
import os.path as osp
import sys
import re
import pdb
import time
from collections import defaultdict


sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/utils')
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from Interpretation import goal_interpretation,exploration_VH
from solver import goal_solver
from auto_debugger import auto_debug
from concepts.dm.crow.parsers.cdl_parser import TransformationError
from concepts.dm.crow.executors.crow_executor import ResampleError

def remove_special_characters(input_string):
    allowed_characters = {',', ':', '(', ')', '_', '#', ' ', '\n','!=','=','[',']'}
    remove_s=''.join(char for char in input_string if char.isalnum() or char in allowed_characters)
    remove_s=remove_s.replace("python"," ")
    pattern = r'(observe\([^,]+,\s*)([^"()]+)(\))'
    remove_s = re.sub(pattern, r'\1"\2"\3', remove_s)
    remove_s=remove_s.replace("plaintext","")
    remove_s=remove_s.replace("'''","")
    return remove_s


def find_behavior_from_library_origin(goal_representation, behavior_from_library):
    """
    Args:
        goal_representation: The goal representation which may contain behavior definitions and calls.
        behavior_from_library: A dictionary containing behaviors and their metadata:
            - 'content': list of behavior definitions.
            - 'names': list of behavior names.
            - 'function_calls': list of dictionaries with keys 'behavior_name' and 'function_calls' (list of functions called by the behavior).
            - 'behavior_calls': list of dictionaries with keys 'behavior_name' and 'called_behaviors' (list of behaviors called by the behavior).
            - 'function_definitions': dictionary mapping function names to their definitions (if available).
    Returns:
        full_code: A string containing all necessary behavior and function definitions.
    """
    # Sets to keep track of behaviors and functions to be added
    behaviors_to_add = set()
    processed_behaviors = set()
    functions_to_add = set()
    processed_functions = set()
    
    # Initialize the output strings
    add_behaviors = ''
    add_functions = ''
    
    behaviors_stack=[]
    # Build a mapping from behavior names to their indices for quick lookup
    behavior_name_to_index = {name: idx for idx, name in enumerate(behavior_from_library['names'])}
    
    # First, parse the goal_representation to find behaviors that are already defined
    # Regex pattern to find behavior definitions in goal_representation
    behavior_pattern = r'behavior\s+(\w+)\s*\(.*?\):'
    defined_behaviors = set(re.findall(behavior_pattern, goal_representation))
    
    # Now, find behaviors in the goal_representation that match behaviors in the library
    for behavior_name in behavior_from_library['names']:
        if behavior_name in goal_representation:
            behaviors_to_add.add(behavior_name)
    
    # Remove behaviors that are already defined in current goal_representation
    behaviors_to_add -= defined_behaviors
    
    # Function to process behaviors recursively
    def process_behavior(behavior_name):
        if behavior_name in processed_behaviors or behavior_name in defined_behaviors:
            return ''
        processed_behaviors.add(behavior_name)
        
        idx = behavior_name_to_index.get(behavior_name)
        if idx is None:
            return ''  # Behavior not found in the library
        
        # Add behavior content
        nonlocal behaviors_stack
        behaviors_stack.append(behavior_from_library['content'][idx])
        
        # Add functions called by this behavior
        called_functions = behavior_from_library['function_calls'][idx]['function_calls']
        for func_name in called_functions:
            functions_to_add.add(func_name)
        
        # Recursively process behaviors called by this behavior
        called_behaviors = behavior_from_library['behavior_calls'][idx]['behavior_calls']
        for called_behavior in called_behaviors:
            process_behavior(called_behavior)
    
    # Process all behaviors that need to be added
    for behavior_name in behaviors_to_add:
        process_behavior(behavior_name)
    
    # Now process functions
    function_pattern = r'function\s+(\w+)\s*\(.*?\):'
    defined_functions = set(re.findall(function_pattern, goal_representation))
    for function_content in functions_to_add:
        if function_content in processed_functions or function_content in defined_functions:
            continue
        add_functions += function_content + '\n'

    behaviors_stack.reverse()
    for behavior_content in behaviors_stack:
        add_behaviors += behavior_content + '\n'
    
    # Combine functions and behaviors
    full_code = add_functions + add_behaviors
    return full_code

def find_behavior_from_library(goal_representation, behavior_from_library):
    """
    Args:
        goal_representation: The goal representation which may contain behavior definitions and calls.
        behavior_from_library: A dictionary containing behaviors and their metadata:
            - 'content': list of behavior definitions.
            - 'names': list of behavior names.
            - 'function_calls': list of dictionaries with keys 'behavior_name' and 'function_calls' (list of functions called by the behavior).
            - 'behavior_calls': list of dictionaries with keys 'behavior_name' and 'behavior_calls' (list of behaviors called by the behavior).
            - 'function_definitions': dictionary mapping function names to their definitions (if available).
    Returns:
        full_code: A string containing all necessary behavior and function definitions.
    """


    # Regex patterns to find definitions
    behavior_def_pattern = r'\bbehavior\s+(\w+)\s*\(.*?\):'
    function_def_pattern = r'\bdef\s+(\w+)\s*\(.*?\):'

    # Find behaviors and functions defined in goal_representation
    defined_behaviors = set(re.findall(behavior_def_pattern, goal_representation))
    defined_functions = set(re.findall(function_def_pattern, goal_representation))

    # Build sets of library behaviors and functions
    library_behaviors = set(behavior_from_library['names'])
    library_functions = set(behavior_from_library['function_definitions'].keys())

    # Find all potential function/behavior calls in goal_representation
    potential_calls = re.findall(r'\b(\w+)\s*\(', goal_representation)

    called_behaviors = set()
    called_functions = set()
    for name in potential_calls:
        if name in library_behaviors and name not in defined_behaviors:
            called_behaviors.add(name)
        elif name in library_functions and name not in defined_functions:
            called_functions.add(name)

    # Build a mapping from behavior names to their indices for quick lookup
    behavior_name_to_index = {name: idx for idx, name in enumerate(behavior_from_library['names'])}

    # Initialize the dependency graph
    dependency_graph = defaultdict(set)  # Node -> set of dependencies

    processed_behaviors = set()

    def process_behavior(behavior_name):
        if behavior_name in processed_behaviors or behavior_name in defined_behaviors:
            return
        processed_behaviors.add(behavior_name)

        idx = behavior_name_to_index.get(behavior_name)
        if idx is None:
            return  # Behavior not found in the library

        # Get the behaviors and functions called by this behavior
        behavior_calls = behavior_from_library['behavior_calls'][idx]['behavior_calls']
        function_calls = behavior_from_library['function_calls'][idx]['function_calls']

        # Filter out behaviors/functions that are already defined
        behavior_dependencies = [b for b in behavior_calls if b not in defined_behaviors]
        function_dependencies = [f for f in function_calls if f not in defined_functions]

        # Add dependencies in the graph
        dependency_graph[behavior_name].update(behavior_dependencies)
        dependency_graph[behavior_name].update(function_dependencies)

        # Ensure the called functions are in the graph (with no dependencies)
        for function_name in function_dependencies:
            if function_name not in dependency_graph:
                dependency_graph[function_name]

        # Process dependencies recursively
        for called_behavior in behavior_dependencies:
            process_behavior(called_behavior)

    # Process called behaviors
    for behavior_name in called_behaviors:
        process_behavior(behavior_name)

    # Add called functions to the dependency graph
    for function_name in called_functions:
        if function_name not in defined_functions:
            if function_name not in dependency_graph:
                dependency_graph[function_name]

    # Perform a topological sort
    visited = set()
    temp_mark = set()
    ordering = []

    def visit(node):
        if node in visited:
            return
        if node in temp_mark:
            raise ValueError("Cyclic dependency detected involving {}".format(node))

        temp_mark.add(node)
        for dep in dependency_graph[node]:
            visit(dep)
        temp_mark.remove(node)
        visited.add(node)
        ordering.append(node)

    for node in dependency_graph:
        if node not in visited:
            visit(node)

    # Reverse the ordering to get the correct sequence
    ordering = ordering[::-1]

    # Assemble the code in the correct order
    full_code = ''
    for node in ordering:
        if node in defined_behaviors or node in defined_functions:
            continue  # Skip if already defined in goal_representation

        if node in library_behaviors:
            # Get behavior content
            idx = behavior_name_to_index.get(node)
            if idx is not None:
                behavior_content = behavior_from_library['content'][idx]
                full_code += behavior_content + '\n'
        elif node in library_functions:
            # Get function content
            function_content = behavior_from_library['function_definitions'].get(node)
            if function_content:
                full_code += function_content + '\n'

    return full_code


def VH_pipeline(state_file:str,execute_file:str,current_subgoal:str,add_info:str,long_horizon_goal:str,sub_goal_list:list,classes,behavior_from_library,behavior_from_library_embedding,partial_observation=True, agent_type="Planning", refinement=True,logger=None):
    """
    Args:
    state_file: Path to the file containing the current state for CDL planning
    execute_file: Path of the file containing the CDL code to be executed
    current_subgoal: The current subgoal to be achieved
    add_info: Additional information for the current subgoal
    long_horizon_goal: The long horizon goal to be achieved
    sub_goal_list: List of subgoals to be achieved
    classes: List of classes
    partial_observation: Whether the observation is partial or not
    """
    exploration_content=''
    generate_time=0

    generate_times_limit=3
    correct_times_limit=2

    if refinement:
        generate_times_limit=generate_times_limit*correct_times_limit
        correct_times_limit=1

    while generate_time<generate_times_limit:
        try:
            goal_int=goal_interpretation(current_subgoal,add_info,long_horizon_goal,classes,sub_goal_list,behavior_from_library_embedding, agent_type)

            goal_int=remove_special_characters(goal_int)

            with open(state_file, "r") as file:
                original_content = file.read()
            combined_content = original_content + "\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            new_file_path = execute_file
            with open(new_file_path, "w") as file:
                file.write(combined_content)

            # Add exploration behaviors
            if partial_observation and exploration_content=='':
                exp_start_time=time.time()
                exploration_content=exploration_VH(current_subgoal,add_info,new_file_path)
                exp_end_time=time.time()
                print(f"Time for exploration:{exp_end_time-exp_start_time:.2f}s")
                exploration_content=remove_special_characters(exploration_content)

            add_behavior_from_library=find_behavior_from_library(goal_int,behavior_from_library)
            if len(add_behavior_from_library) > 0:
                logger.info("Use behavior from library:\n"+add_behavior_from_library)
            combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            correct_time=0

            logger.info("Goal representation from planning.py\n"+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n")


            while correct_time < correct_times_limit:
                try:
                    if agent_type=="Planning":
                        plan=goal_solver(new_file_path, planning=True)
                    else: # Policy
                        plan=goal_solver(new_file_path, planning=False)
                    if partial_observation:
                        return plan,goal_int,exploration_content,add_behavior_from_library
                    else:
                        return plan,goal_int,add_behavior_from_library

                except TransformationError as e:
                    if refinement:
                        error_info=e.errors
                        print("Error information: ",error_info)
                        logger.info("Inner TransformationError Debug\n"+error_info)
                        with open(new_file_path, "r") as file:
                            for line_number, line in enumerate(file, start=1):
                                if '#goal_representation\n' in line:
                                    goal_start_line_num=line_number
                                    break
                        goal_int=auto_debug(error_info,original_content,goal_int,current_subgoal,add_info,classes,goal_start_line_num,behavior_from_library,agent_type)
                        goal_int=remove_special_characters(goal_int)

                        if partial_observation:
                            exploration_content=exploration_VH(current_subgoal,add_info,new_file_path)
                            exploration_content=remove_special_characters(exploration_content)
                        add_behavior_from_library=find_behavior_from_library(goal_int,behavior_from_library)

                        if len(add_behavior_from_library) > 0:
                            logger.info("Use behavior from library:\n"+add_behavior_from_library)

                        combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
                        with open(new_file_path, "w") as file:
                            file.write(combined_content)
                        correct_time+=1
                        logger.info("Goal representation after debugging in planning.py"+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n")
                    else:
                        break

        except TransformationError as e:

            error_info=e.errors
            print("Error information: ",error_info)
            logger.info("Outer TransformationError Debug\n"+"\nError info:\n"+error_info)
            generate_time+=1
            print("Generate time: ",generate_time)

        except ResampleError as e:

            error_info=e.errors
            print("Error information: ",error_info)
            logger.info("ResampleError Debug\n"+"\nError info:\n"+error_info)
            generate_time+=1
            print("Generate time: ",generate_time)


        except Exception as e:
            error_info=e.errors
            print("Error information: ",e)
            logger.info("Exception Debug"+"\nError info:\n"+error_info)
            generate_time+=1
            print("Generate time: ",generate_time)
    print("debug")
    return None,None,None,None  


goal_representation = '''
behavior main_behavior():
    behavior_b()
    function_z()
'''

# Sample behavior_from_library with behaviors and functions
behavior_from_library = {
    'names': ['behavior_a', 'behavior_b', 'behavior_c'],
    'content': [
        '''
behavior behavior_a():
    function_x()
''',
        '''
behavior behavior_b():
    behavior_a()
    function_y()
''',
        '''
behavior behavior_c():
    behavior_b()
    function_w()
'''
    ],
    'function_calls': [
        {'behavior_name': 'behavior_a', 'function_calls': ['function_x']},
        {'behavior_name': 'behavior_b', 'function_calls': ['function_y']},
        {'behavior_name': 'behavior_c', 'function_calls': ['function_w']},
    ],
    'behavior_calls': [
        {'behavior_name': 'behavior_a', 'behavior_calls': []},
        {'behavior_name': 'behavior_b', 'behavior_calls': ['behavior_a']},
        {'behavior_name': 'behavior_c', 'behavior_calls': ['behavior_b']},
    ],
    'function_definitions': {
        'function_x': '''
def function_x():
    # Implementation of function_x
''',
        'function_y': '''
def function_y():
    # Implementation of function_y
''',
        'function_w': '''
def function_w():
    # Implementation of function_w
''',
        'function_z': '''
def function_z():
    # Implementation of function_z
'''
    }
}

# start_time = time.time()
# full_code = find_behavior_from_library(goal_representation, behavior_from_library)
# end_time = time.time()
# print(f"Time taken: {end_time - start_time:.2f}s")
# print("Generated Code:")
# print(full_code)