import json
import os.path as osp
import sys

sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/embodied-agent-eval/src/VIRTUALHOME/AgentEval-main')
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/utils')

import virtualhome_eval.simulation.evolving_graph.utils as utils
from virtualhome_eval.simulation.evolving_graph.eval_utils import *
import virtualhome_eval.evaluation.action_sequence.prompts.one_shot as one_shot
from virtualhome_eval.evaluation.action_sequence.scripts.utils_lpq import get_nodes_information,construct_cdl,get_from_dataset
from Interpretation import goal_interpretation,refiner,feedbackloop,exploration_VH
from solver import goal_solver
from auto_debugger import auto_debug
from concepts.dm.crow.parsers.cdl_parser import TransformationError

def remove_special_characters(input_string):
    allowed_characters = {',', ':', '(', ')', '_', '#', ' ', '\n','!=','=','[',']'}
    remove_s=''.join(char for char in input_string if char.isalnum() or char in allowed_characters)
    remove_s=remove_s.replace("python"," ")
    return remove_s

def VH_pipeline(goal,add_info,classes,partial_observation=True):
    exploration_content = ""
    # objects,states,relationships,properties,categories,classes,cat_statement=get_nodes_information(scene_graph)
    # construct_cdl(objects,states,relationships,properties,cat_statement)
    exploration_content=''
    generate_time=0
    while generate_time<5:
        try:
            goal_int=goal_interpretation(goal,add_info,classes)
            goal_int=remove_special_characters(goal_int)
            with open("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/init_scene.cdl", "r") as file:
                original_content = file.read()
            combined_content = original_content + "\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            new_file_path = "/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/exicutable_cdl.cdl"
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            if partial_observation and exploration_content=='':#replan exploration behaviors
                exploration_content=exploration_VH(goal,add_info,new_file_path)
                exploration_content=remove_special_characters(exploration_content)
            combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
            with open(new_file_path, "w") as file:
                file.write(combined_content)
            print(f"Combined content saved to {new_file_path}")
            loop=False
            correct_time=0
            while correct_time < 5:
                try:
                    plan=goal_solver(original_content + "\n" + goal_int)
                    if loop:
                        if len(plan)==0:
                            break
                        if len(plan)>0:
                            print('=' * 80)
                            print("goal representation before loop:")
                            print('=' * 80)
                            print(goal_int)
                            goal_int=feedbackloop(goal,add_info,
                            classes,goal_int,plan[0])
                            goal_int=remove_special_characters(goal_int)
                            with open(new_file_path, "w") as file:
                                    combined_content = original_content + "\n" + goal_int
                                    file.write(combined_content)
                            
                            # exploration_content=exploration(goal,additional_information,new_file_path)
                            # exploration_content=remove_special_characters(exploration_content)
                            combined_content=original_content+"\n"+"\n#goal_representation\n"+goal_int+"\n#goal_representation_end\n"
                            with open(new_file_path, "w") as file:
                                file.write(combined_content)
                            plan_afterloop=goal_solver(original_content + "\n" + goal_int)
                            
                            if len(plan_afterloop)==0:
                                break
                            if len(plan_afterloop)>0:
                                print('=' * 80)
                                print("Plan found.")
                                print('=' * 80)
                                print("Goal representation:")
                                print(goal_int)
                                print('=' * 80)
                                
                                return plan_afterloop,goal_int
                    else:
                        if partial_observation:
                            return plan,goal_int,exploration_content
                        else:
                            return plan,goal_int


                except TransformationError as e:
                    error_info=e.errors
                    print("Error information: ",error_info)
                    goal_int=auto_debug(error_info,original_content,goal_int,goal,add_info,classes)
                    goal_int=remove_special_characters(goal_int)
                    if partial_observation:
                        exploration_content=exploration_VH(goal,add_info,new_file_path)
                        exploration_content=remove_special_characters(exploration_content)
                    combined_content=original_content+"\n#exp_behavior\n"+exploration_content+'\n#exp_behavior_end\n'"\n#goal_representation\n" + goal_int+"\n#goal_representation_end\n"
                    with open(new_file_path, "w") as file:
                        file.write(combined_content)
                    correct_time+=1

        except TransformationError as e:
            error_info=e.errors
            print("Error information: ",error_info)
            generate_time+=1