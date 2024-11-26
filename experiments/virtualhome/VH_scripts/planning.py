import json
import os.path as osp
import sys
import re
import pdb
import time


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


def find_behavior_from_library(goal_representation, behavior_from_library):
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
    
    # Remove behaviors that are already defined in goal_representation
    behaviors_to_add -= defined_behaviors
    
    # Function to process behaviors recursively
    def process_behavior(behavior_name):
        if behavior_name in processed_behaviors or behavior_name in defined_behaviors:
            return
        processed_behaviors.add(behavior_name)
        
        idx = behavior_name_to_index.get(behavior_name)
        if idx is None:
            return  # Behavior not found in the library
        
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


# def find_behavior_from_library(goal_representation, behavior_from_library):
#     """
#     Args:
#         goal_representation: The goal representation which may contain behavior calls.
#         behavior_from_library: A dictionary containing behaviors and their metadata:
#             - 'content': list of behavior definitions.
#             - 'names': list of behavior names.
#             - 'function_calls': list of dictionaries with keys 'behavior_name' and 'function_calls' (list of functions called by the behavior).
#             - 'behavior_calls': list of dictionaries with keys 'behavior_name' and 'called_behaviors' (list of behaviors called by the behavior).
#             - 'function_definitions': dictionary mapping function names to their definitions (if available).
#     Returns:
#         full_code: A string containing all necessary behavior and function definitions.
#     """
#     # Sets to keep track of behaviors and functions to be added
#     behaviors_to_add = set()
#     processed_behaviors = set()
#     functions_to_add = set()
    
#     # Initialize the output strings
#     add_behaviors = ''
#     add_functions = ''
    
#     # Build a mapping from behavior names to their indices for quick lookup
#     behavior_name_to_index = {name: idx for idx, name in enumerate(behavior_from_library['names'])}
    
#     # First, find behaviors in the goal_representation that match behaviors in the library
#     for behavior_name in behavior_from_library['names']:
#         if behavior_name in goal_representation:
#             behaviors_to_add.add(behavior_name)
    
#     # Function to process behaviors recursively
#     def process_behavior(behavior_name):
#         if behavior_name in processed_behaviors:
#             return
#         processed_behaviors.add(behavior_name)
        
#         idx = behavior_name_to_index.get(behavior_name)
#         if idx is None:
#             return  # Behavior not found in the library
        
#         # Add behavior content
#         nonlocal add_behaviors
#         add_behaviors += behavior_from_library['content'][idx] + '\n'
        
#         # Add functions called by this behavior
#         called_functions = behavior_from_library['function_calls'][idx]['function_calls']
#         for func_content in called_functions:
#             functions_to_add.add(func_content)
        
#         # Recursively process behaviors called by this behavior
#         called_behaviors = behavior_from_library['behavior_calls'][idx]['behavior_calls']
#         for called_behavior in called_behaviors:
#             process_behavior(called_behavior)
    
#     # Process all behaviors that need to be added
#     for behavior_name in behaviors_to_add:
#         process_behavior(behavior_name)
    
#     # Now process functions
#     for func_content in functions_to_add:
#             add_functions += func_content + '\n'

#     # Combine functions and behaviors
#     full_code = add_functions + add_behaviors
#     return full_code


def VH_pipeline(state_file:str,execute_file:str,current_subgoal:str,add_info:str,long_horizon_goal:str,sub_goal_list:list,classes,behavior_from_library,behavior_from_library_embedding,partial_observation=True, agent_type="Planning", refinement=True):
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
            # logger.info("Goal representation",goal_int)

            with open(state_file, "r") as file:
                original_content = file.read()
            combined_content = original_content + "\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            new_file_path = execute_file
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            if partial_observation and exploration_content=='':#replan exploration behaviors
                # pdb.set_trace()
                # Timmer
                exp_start_time=time.time()
                exploration_content=exploration_VH(current_subgoal,add_info,new_file_path)
                exp_end_time=time.time()
                print(f"Time for exploration:{exp_end_time-exp_start_time:.2f}s")
                exploration_content=remove_special_characters(exploration_content)

            add_behavior_from_library=find_behavior_from_library(goal_int,behavior_from_library)
            combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            loop=False
            correct_time=0
            while correct_time < correct_times_limit:
                try:
                    # pdb.set_trace()
                    solver_start_time=time.time()
                    if agent_type=="Planning":
                        plan=goal_solver(new_file_path, planning=True)
                    else: # Policy
                        plan=goal_solver(new_file_path, planning=False)
                    solver_end_time=time.time()
                    # print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")
                    # logger.info(goal_int,"","","","",plan)
                    if loop:
                        pass
                    else:
                        if partial_observation:
                            return plan,goal_int,exploration_content,add_behavior_from_library
                        else:
                            return plan,goal_int,add_behavior_from_library

                except TransformationError as e:
                    if refinement:
                        solver_end_time=time.time()
                        # print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")
                        error_info=e.errors
                        # print("Error information: ",error_info)
                        # logger.info(goal_int,error_info,"","","","")
                        with open(new_file_path, "r") as file:
                            for line_number, line in enumerate(file, start=1):
                                if '#goal_representation\n' in line:
                                    goal_start_line_num=line_number
                                    break
                        goal_int=auto_debug(error_info,original_content,goal_int,current_subgoal,add_info,classes,goal_start_line_num,behavior_from_library,agent_type)
                        goal_int=remove_special_characters(goal_int)
                        # logger.info("Goal representation after debugging",goal_int)
                        if partial_observation:
                            exploration_content=exploration_VH(current_subgoal,add_info,new_file_path)
                            exploration_content=remove_special_characters(exploration_content)
                        add_behavior_from_library=find_behavior_from_library(goal_int,behavior_from_library)
                        combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
                        with open(new_file_path, "w") as file:
                            file.write(combined_content)
                        correct_time+=1
                    else:
                        break

        except TransformationError as e:
            solver_end_time=time.time()
            # print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")

            error_info=e.errors
            print("Error information: ",error_info)
            # logger.info("Error information: ",error_info)

            generate_time+=1
            print("Generate time: ",generate_time)

        except ResampleError as e:
            solver_end_time=time.time()
            # print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")

            error_info=e.errors
            print("Error information: ",error_info)
            # logger.info("Error information: ",error_info)
            generate_time+=1
            print("Generate time: ",generate_time)


        except Exception as e:
            solver_end_time=time.time()
            # print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")

            print("Error information: ",e)
            # logger.info("Error information: ",e)
            generate_time+=1
            print("Generate time: ",generate_time)
    print("debug")
    return None,None,None,None  
