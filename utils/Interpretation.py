import re
from prompt.ask_GPT import ask_GPT
from prompt.goal_interpretation_prompt import get_goal_inter_prompt
# from prompt.kitchen_prompt import get_goal_inter_prompt
# from prompt.kitchen_loopfeedback import loop_refine
from prompt.exploration_prompt import get_exp_behavior
# from auto_debugger import exploration_auto_debug
from prompt.sub_goal_split_prompt import sub_goal_prompt
from prompt.sub_goal_evaluate_prompt import sub_goal_evaluate_prompt
from prompt.obs_query_prompt import obs_query_prompt
import sys
sys.path.append('experiments/virtualhome/VH_scripts')
from logger import logger

from prompt.QA.exp_helper_prompt import Exp_helper_prompt

def parse_evaluation(evaluation_text):
    sub_task_completed_match = re.search(r"Sub-Task Completed:\s*(Yes|No)", evaluation_text)
    if sub_task_completed_match:
        sub_task_completed = sub_task_completed_match.group(1)
    else:
        raise ValueError("not find the value of 'Sub-Task Completed'")
    
    next_steps_match = re.search(r"Next Steps:\s*(.*)", evaluation_text)
    if next_steps_match:
        next_steps = next_steps_match.group(1).strip()
        if sub_task_completed == "Yes":
            next_steps = "None"  
    else:
        raise ValueError("not find the value of 'Sub-Task Completed'")

    
    return sub_task_completed, next_steps

def goal_interpretation(goal,additional_information,long_horizon_goal,item_list=None,sub_tasks_list=None):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system = "I have a goal described in natural language, and I need it converted into a structured format."
    content = get_goal_inter_prompt(goal,item_list,additional_information,long_horizon_goal,sub_tasks_list)

    print('=' * 80)
    print(f"When Goal instruction is: {goal}")
    converted_content=ask_GPT(system,content)
    print('=' * 80)

    return converted_content

# def feedbackloop(goal,additional_information,item_list=None,goal_representation=None,action_seq=None):
#     if ":item" in item_list[0]:
#         for item in item_list:
#             item=item.replace(":item",'')
#     system="You are a patient, meticulous, and keenly observant grammar expert. Based on the action sequences I generate, along with my goals and additional information, I need you to reverse-engineer and refine my goal representation."
#     content=loop_refine(goal,item_list,additional_information,action_seq,goal_representation)
#     print('=' * 80)
#     print(f"Loop feedback:")
#     print('=' * 80)
#     refined_content=ask_GPT(system,content)
#     print('=' * 80)
#     return refined_content



def exploration_VH(goal,additional_information,problem_cdl,checked=None):
    print('=' * 80)
    print(f"Exploration:")
    print('=' * 80)
    exp_behavior=get_exp_behavior(goal,additional_information,problem_cdl,checked)
    print('=' * 80)
    return exp_behavior

def sub_goal_generater(goal):
    system="You are a assistant robot. Your work is to decompose the goal into sub-goals."
    print('=' * 80)
    print(f"Sub goal generation:")
    print('=' * 80)
    content=sub_goal_prompt(goal)
    sub_goals=ask_GPT(system,content)
    print('=' * 80)
    if '\n' in sub_goals:
        sub_goal_list=sub_goals.split("\n")
    else:
        sub_goal_list=[sub_goals]
    return sub_goal_list

def obs_query(observation,target_obj,question):
    system="You are a AI assistant. Your work is to briefly answer the question based on your observation."
    print('=' * 80)
    print(f"Observation query:")
    content=obs_query_prompt(observation,target_obj,question)
    answer=ask_GPT(system,content)
    print(answer)
    logger.info('','','','',answer,'')
    print('=' * 80)
    return answer

def sub_goal_evaluate(goal_representation,action_history,current_subgoal,full_goal, next_subgoal,collected_information,obj_list):
    system="You are a AI assistant. Your work is to evaluate whether the current sub-task has been completed."
    print('=' * 80)
    print(f"Sub goal evaluation:")
    content=sub_goal_evaluate_prompt(goal_representation,action_history,current_subgoal,full_goal, next_subgoal,collected_information,obj_list)
    evaluation=ask_GPT(system,content)
    result, next_instructions = parse_evaluation(evaluation)
    print(evaluation)
    logger.info('','','','',evaluation,'')
    print('=' * 80)
    return result, next_instructions

def Exp_helper(target_obj,discription):
    system="You are the owner of the house. Your home robot is searching for an item. I need you to clearly and concisely tell the robot where it can find the target item based on the information you have."
    content=Exp_helper_prompt(target_obj,discription)
    print('=' * 80)
    print(f"Human Exp_helper:")
    res=ask_GPT(system,content)
    print('=' * 80)
    return res


if __name__=='__main__':
    goal='Make chicken pasta.'
    sub_goal_list=sub_goal_generater(goal)
    print(sub_goal_list)