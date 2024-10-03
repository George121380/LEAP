import json
import os.path as osp
import sys
import re
import pdb
import time


sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/utils')
from logger import logger
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
    return remove_s

def find_behavior_from_library(goal_representation,behavior_from_library):
    # goal_representation may contains behaviors from library, this function will find the behaviors from library
    add_behaviors=''
    pattern = re.compile(r'(\w+)\s*\(.*?:.*?\)')
    for idx in range(len(behavior_from_library['names'])):
        behavior_name=pattern.findall(behavior_from_library['names'][idx])
        if behavior_name:
            behavior_name=behavior_name[0]
            if behavior_name in goal_representation:
                add_behaviors+=behavior_from_library['content'][idx]+'\n'
    return add_behaviors


def VH_pipeline(state_file:str,execute_file:str,current_subgoal:str,add_info:str,long_horizon_goal:str,sub_goal_list:list,classes,behavior_from_library,partial_observation=True):
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
    while generate_time<3:
        try:
            goal_int=goal_interpretation(current_subgoal,add_info,long_horizon_goal,classes,sub_goal_list,behavior_from_library['names'])

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
            while correct_time < 3:
                try:
                    # pdb.set_trace()
                    solver_start_time=time.time()
                    plan=goal_solver(combined_content + "\n" + goal_int)
                    solver_end_time=time.time()
                    # print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")
                    logger.info(goal_int,"","","","",plan)
                    if loop:
                        pass
                    else:
                        if partial_observation:
                            return plan,goal_int,exploration_content,add_behavior_from_library
                        else:
                            return plan,goal_int,add_behavior_from_library

                except TransformationError as e:
                    solver_end_time=time.time()
                    print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")
                    error_info=e.errors
                    # print("Error information: ",error_info)
                    logger.info(goal_int,error_info,"","","","")
                    with open(new_file_path, "r") as file:
                        for line_number, line in enumerate(file, start=1):
                            if '#goal_representation\n' in line:
                                goal_start_line_num=line_number
                                break
                    goal_int=auto_debug(error_info,original_content,goal_int,current_subgoal,add_info,classes,goal_start_line_num,behavior_from_library)
                    goal_int=remove_special_characters(goal_int)
                    # logger.info("Goal representation after debugging",goal_int)
                    if partial_observation:
                        exploration_content=exploration_VH(current_subgoal,add_info,new_file_path)
                        exploration_content=remove_special_characters(exploration_content)
                    combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'+"\n#behaviors_from_library\n"+add_behavior_from_library+"\n#behaviors_from_library_end\n"+"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
                    with open(new_file_path, "w") as file:
                        file.write(combined_content)
                    correct_time+=1

        except TransformationError as e:
            solver_end_time=time.time()
            print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")

            error_info=e.errors
            print("Error information: ",error_info)
            # logger.info("Error information: ",error_info)

            generate_time+=1
            print("Generate time: ",generate_time)

        except ResampleError as e:
            solver_end_time=time.time()
            print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")

            error_info=e.errors
            print("Error information: ",error_info)
            # logger.info("Error information: ",error_info)
            generate_time+=1
            print("Generate time: ",generate_time)


        except Exception as e:
            solver_end_time=time.time()
            print(f"Time for solving:{solver_end_time-solver_start_time:.4f}s")

            print("Error information: ",e)
            # logger.info("Error information: ",e)
            generate_time+=1
            print("Generate time: ",generate_time)
