import json
import os.path as osp
import sys
import re
import pdb
import time
from collections import defaultdict

sys.path.append('embodied-agent-eval/src/VIRTUALHOME/AgentEval-main')
sys.path.append('utils')
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
from Interpretation import goal_interpretation,exploration_VH, refinement_loop_feedback
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

def refinement_operation(goal_int:str,correct_times_limit:int,state_file:str,execute_file:str,current_subgoal:str,add_info:str,long_horizon_goal:str,prev_sub_goal_list:list,classes,behavior_from_library,partial_observation=True, agent_type="Planning", refinement=True,loop_feedback=False,logger=None):
    with open(state_file, "r") as file:
        original_content = file.read()
    combined_content = original_content + "\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
    new_file_path = execute_file
    with open(new_file_path, "w") as file:
        file.write(combined_content)

    exploration_content=''
    # Add exploration behaviors
    if partial_observation and exploration_content=='':
        exp_start_time=time.time()
        exploration_content=exploration_VH(current_subgoal,add_info,new_file_path)
        exp_end_time=time.time()
        print(f"Time for exploration:{exp_end_time-exp_start_time:.2f}s")
        exploration_content=remove_special_characters(exploration_content)

    combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
    with open(new_file_path, "w") as file:
        file.write(combined_content)
    correct_time=0

    logger.info("Goal representation from planning.py\n"+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n")

    while correct_time < correct_times_limit:
        try:
            if agent_type=="Planning":
                plan=goal_solver(new_file_path, planning=True)
            else: # Policy
                plan=goal_solver(new_file_path, planning=False)

            if loop_feedback:
                refinement_loop_feedback(plan,long_horizon_goal,prev_sub_goal_list,current_subgoal,behavior_from_library, goal_int, add_info, classes, agent_type)

            if partial_observation:
                return plan,goal_int,exploration_content
            else:
                return plan,goal_int,''

        except Exception as e:
            # Refine after error
            if refinement:
                try:
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

                    combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
                    with open(new_file_path, "w") as file:
                        file.write(combined_content)
                    correct_time+=1
                    logger.info("Goal representation after debugging in planning.py"+"\n#exp_behavior\n"+exploration_content+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n")
                except AttributeError:
                    logger.info(f"Error is:\n{e}")
                    print(f"Error is:\n{e}")
                    print("e does not have an 'error' attribute. Directly resample")
                    return None,None,None
            else:
                return None,None,None
    

def VH_pipeline(state_file:str,execute_file:str,current_subgoal:str,add_info:str,long_horizon_goal:str,prev_sub_goal_list:list,classes,behavior_from_library,partial_observation=True, agent_type="Planning", refinement=True,loop_feedback=False,logger=None):
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
    generate_time=0

    generate_times_limit=3
    correct_times_limit=2

    if not refinement: # If refinement is disabled, make sure the model could resample for equal times
        generate_times_limit=generate_times_limit*correct_times_limit
        correct_times_limit=1

    while generate_time<generate_times_limit:

        goal_int=goal_interpretation(current_subgoal,add_info,long_horizon_goal,classes,prev_sub_goal_list,behavior_from_library, agent_type)
        goal_int=remove_special_characters(goal_int)

        if refinement:
            plan,goal_int,exploration_content=refinement_operation(goal_int,correct_times_limit,state_file,execute_file,current_subgoal,add_info,long_horizon_goal,prev_sub_goal_list,classes,behavior_from_library,partial_observation, agent_type, refinement,loop_feedback,logger)
            return plan,goal_int,exploration_content
        
    print("debug")
    return None,None,None  