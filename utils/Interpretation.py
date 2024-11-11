import re
from prompt.ask_GPT import ask_GPT
from prompt.planning_goal_interpretation_prompt import get_planning_goal_inter_prompt
from prompt.policy_goal_interpretation_prompt import get_policy_goal_inter_prompt

# from prompt.kitchen_prompt import get_goal_inter_prompt
# from prompt.kitchen_loopfeedback import loop_refine
from prompt.exploration_prompt import get_exp_behavior
# from auto_debugger import exploration_auto_debug
# from prompt.sub_goal_split_prompt import sub_goal_prompt
from prompt.sub_goal_split_finer_prompt import sub_goal_prompt
from prompt.sub_goal_evaluate_prompt import sub_goal_evaluate_prompt
from prompt.obs_query_prompt import obs_query_prompt
import sys
sys.path.append('experiments/virtualhome/VH_scripts')
import time

from prompt.QA.exp_helper_prompt import Exp_helper_prompt
from prompt.QA.guidance_helper_prompt import Guidance_helper_prompt

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

def goal_interpretation(goal,additional_information,long_horizon_goal,item_list=None,sub_tasks_list=None,behavior_from_library_names=None, agent_type='Planning'):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system = "I have a goal described in natural language, and I need it converted into a structured format."
    if agent_type=='Planning':
        content = get_planning_goal_inter_prompt(goal,item_list,additional_information,long_horizon_goal,sub_tasks_list,behavior_from_library_names)
    if agent_type=='Policy':
        content = get_policy_goal_inter_prompt(goal,item_list,additional_information,long_horizon_goal,sub_tasks_list,behavior_from_library_names)
    start_time=time.time()
    print('=' * 60+ " Goal CDL Generation")
    print(f"When Goal instruction is: {goal}")
    converted_content=ask_GPT(system,content)
    end_time=time.time()
    print('=' * 60+ " time:",f"{end_time-start_time:.2f}s")

    return converted_content

def exploration_VH(goal,additional_information,problem_cdl,checked=None):
    # print('=' * 60)
    # print(f"Exploration:")
    # print('=' * 60)
    exp_behavior=get_exp_behavior(goal,additional_information,problem_cdl,checked)
    # print('=' * 60)
    return exp_behavior

def sub_goal_generater(goal,completed_sub_goal_list,human_guidance):
    # system="You are a assistant robot. Your work is to decompose the goal into sub-goals."
    system="You are an intelligent task planner with expert knowledge in task breakdown, goal evaluation, and human-robot collaboration. Your role is to evaluate whether a given task goal needs to be split into subgoals or if it can be directly pursued. You consider the overall goal of the task, previously completed subgoals, and any human guidance provided. Based on your evaluation, you either generate a set of subgoals that help the task progress more efficiently or output the next most appropriate goal. Your output should always be logically sound, concise, and relevant to the task at hand."
    print('=' * 60)
    print(f"Sub goal generation:")
    print('=' * 60)
    content=sub_goal_prompt(goal,completed_sub_goal_list,human_guidance)
    sub_goals=ask_GPT(system,content)
    print('=' * 60)
    if 'No decomposition:' in sub_goals:
        sub_goal_list=[sub_goals.replace('No decomposition:','').strip()]
    else:
        sub_goal_list=sub_goals.split("\n")
    return sub_goal_list

def obs_query(observation,target_obj,question):
    system="You are a AI assistant. Your work is to briefly answer the question based on your observation."
    print('=' * 60)
    print(f"Observation query:")
    content=obs_query_prompt(observation,target_obj,question)
    answer=ask_GPT(system,content)
    print(answer)
    # logger.info('','','','',answer,'')
    print('=' * 60)
    return answer

def sub_goal_evaluate(goal_representation,action_history,current_subgoal,full_goal, next_subgoal,collected_information,obj_list):
    system="You are a AI assistant. Your work is to evaluate whether the current sub-task has been completed."
    print('=' * 60)
    print(f"Sub goal evaluation:")
    content=sub_goal_evaluate_prompt(goal_representation,action_history,current_subgoal,full_goal, next_subgoal,collected_information,obj_list)
    evaluation=ask_GPT(system,content)
    result, next_instructions = parse_evaluation(evaluation)
    print(evaluation)
    # logger.info('','','','',evaluation,'')
    print('=' * 60)
    return result, next_instructions

def Exp_helper(target_obj,discription):
    system="You are the owner of the house. Your home robot is searching for an item. I need you to clearly and concisely tell the robot where it can find the target item based on the information you have."
    content=Exp_helper_prompt(target_obj,discription)
    print('=' * 60)
    print(f"Human Exp_helper:")
    res=ask_GPT(system,content)
    print('=' * 60)
    return res

def Guidance_helper(question,knowledge):
    system="You are the owner of a room, and at this moment, your household robot is encountering some difficulties while completing its task. Based on your knowledge, please guide the household robot to finish the task."
    print('=' * 60)
    print(f"Human Guidance_helper:")
    content=Guidance_helper_prompt(question,knowledge)
    res=ask_GPT(system,content)
    print('=' * 60)
    print(res)
    return res

if __name__=='__main__':
    goal='Wash my t-shirt by the washing machine'
    sub_goal_list=sub_goal_generater(goal,['Find the t-shirt', 'place the t-shirt into the washing machine'],'')
    print(sub_goal_list)
    goal='Turn on the light in the bathroom'
    sub_goal_list=sub_goal_generater(goal,[],'')
    print(sub_goal_list)
    print(len(sub_goal_list))

    goal='Make salad'
    sub_goal_list=sub_goal_generater(goal,[],'')
    print(sub_goal_list)