import re
from prompt.check_unknown_variable import not_found_prompt,unknown_prompt,other_prompt
from concepts.dm.crow.parsers.cdl_parser import TransformationError
from Interpretation import ask_GPT
def auto_debug(error_info,original_content,goal_int,goal,additional_information,cat_list):
    print('=' * 80)
    print("Debugging...")
    print('=' * 80)
    print("Error information: ",error_info)
    if "Unknown variable" in error_info:
        error_variable = re.search(r"Unknown variable:\s*(\w+)", error_info)
        error_variable = error_variable.group(1)
        prompt=unknown_prompt(goal,cat_list,additional_information,goal_int,error_variable)
        system_prompt="You are a meticulous and detailed assistant. I have defined a set of syntax and written a program, Some variables were used before being declared. Please help me supplement their declarations."

    elif "not found" in error_info:
        error_variable = re.search(r'Function (.*?) not found', error_info)
        error_variable = error_variable.group(1)
        prompt=not_found_prompt(goal,cat_list,additional_information,goal_int,error_variable)
        system_prompt="You are a meticulous and detailed assistant. I have defined a set of syntax and written a program, which uses category names outside the specified ones. Please find these category names and replace them."

    else:
        prompt=other_prompt(goal,cat_list,additional_information,goal_int,error_variable)
        system_prompt="I encountered this error while running the program. Please try to correct my mistake based on the syntax rules I provided."
        
    debugged_goal_int=ask_GPT(system_prompt,prompt)
    print('=' * 80)
    print("Debugging finished.")
    print('=' * 80)
    return debugged_goal_int