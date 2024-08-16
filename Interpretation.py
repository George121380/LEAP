import re
from prompt.ask_GPT import ask_GPT
from prompt.goal_interpretation_prompt import get_goal_inter_prompt
# from prompt.kitchen_prompt import get_goal_inter_prompt
from prompt.kitchen_refine_prompt import refine_prompt
from prompt.kitchen_loopfeedback import loop_refine
from prompt.exploration_prompt import get_exp_prompt


# from prompt.refine_prompt import refine_prompt

def goal_interpretation(goal,additional_information,item_list=None):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system = "I have a goal described in natural language, and I need it converted into a structured format."
    content = get_goal_inter_prompt(goal,item_list,additional_information)

    print('=' * 80)
    print(f"When Goal instruction is: {goal}")
    converted_content=ask_GPT(system,content)
    print('=' * 80)

    return converted_content

def refiner(goal,additional_information,item_list=None,goal_representation=None):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system = "You are a patient, meticulous, and keenly observant grammar expert. I need your help to check and correct any errors in a series of form transformations I have made."
    content = refine_prompt(goal,item_list,additional_information,goal_representation)

    print(f"After refined:")

    print('=' * 80)
    converted_content=ask_GPT(system,content)
    print('=' * 80)

    return converted_content

def feedbackloop(goal,additional_information,item_list=None,goal_representation=None,action_seq=None):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system="You are a patient, meticulous, and keenly observant grammar expert. Based on the action sequences I generate, along with my goals and additional information, I need you to reverse-engineer and refine my goal representation."
    content=loop_refine(goal,item_list,additional_information,action_seq,goal_representation)
    print('=' * 80)
    print(f"Loop feedback:")
    print('=' * 80)
    refined_content=ask_GPT(system,content)
    print('=' * 80)
    return refined_content

def exploration(goal,additional_information,problem_cdl):
    system="You are a grammar expert with good common sense. I have some items that I need to find, and I need you to help me design a series of formal representations of find actions based on a set of grammar rules I define and your own common sense."
    content=get_exp_prompt(goal,additional_information,problem_cdl)
    print('=' * 80)
    print(f"Exploration:")
    print('=' * 80)
    exploration_content=ask_GPT(system,content)
    print('=' * 80)
    return exploration_content

def exploration_VH(goal,additional_information,problem_cdl):
    system="You are a grammar expert with good common sense. I have some items that I need to find, and I need you to help me design a series of formal representations of find actions based on a set of grammar rules I define and your own common sense."
    content=get_exp_prompt(goal,additional_information,problem_cdl)
    print('=' * 80)
    print(f"Exploration:")
    print('=' * 80)
    exploration_content=ask_GPT(system,content)
    print('=' * 80)
    return exploration_content