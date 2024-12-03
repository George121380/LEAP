import re
from prompt.planning_auto_debug_prompt import planning_not_found_prompt,planning_unknown_prompt,planning_other_prompt
from prompt.policy_auto_debug_prompt import policy_not_found_prompt,policy_unknown_prompt,policy_other_prompt
from concepts.dm.crow.parsers.cdl_parser import TransformationError
from Interpretation import ask_GPT
def auto_debug(error_info,original_content,goal_int,goal,additional_information,cat_list,goal_start_line_num,behavior_from_library,agent_type):
    print('=' * 80)
    print("Debugging...")
    # print('=' * 80)
    # print("Error information: ",error_info)

    if "Unknown variable" in error_info:
        error_variable = re.search(r"Unknown variable:\s*(\w+)", error_info)
        error_variable = error_variable.group(1)
        if agent_type=='Planning':
            prompt=planning_unknown_prompt(goal,cat_list,additional_information,goal_int,error_variable,behavior_from_library)
        elif agent_type=='Policy':
            prompt=policy_unknown_prompt(goal,cat_list,additional_information,goal_int,error_variable,behavior_from_library)
        else:
            raise TransformationError("Unknown agent type.")
        system_prompt="You are a meticulous and detailed assistant. I have defined a set of syntax and written a program, Some variables were used before being declared. Please help me supplement their declarations."

    elif "not found" in error_info:
        error_variable = re.search(r'Function (.*?) not found', error_info)
        error_variable = error_variable.group(1)
        prompt=planning_not_found_prompt(goal,cat_list,additional_information,goal_int,error_variable)
        system_prompt="You are a meticulous and detailed assistant. I have defined a set of syntax and written a program, which uses category names outside the specified ones. Please find these category names and replace them."
    
    elif "at line" in error_info:
        error_line_num= int(re.search(r'at line (\d+)', error_info).group(1))
        error_line_num=error_line_num-goal_start_line_num
        useful_error_info=error_info.split('\n')[0]
        useful_error_info=re.sub(r'(at line )(\d+)', str(error_line_num), useful_error_info)
        if agent_type=='Planning':
            prompt=planning_other_prompt(goal,cat_list,additional_information,goal_int,useful_error_info,behavior_from_library)
        elif agent_type=='Policy':
            prompt=policy_other_prompt(goal,cat_list,additional_information,goal_int,useful_error_info,behavior_from_library)
        else:
            raise TransformationError("Unknown agent type")
        system_prompt="I encountered this error while running the program. Please try to correct my mistake based on the syntax rules I provided."
        

    else:
        if agent_type=='Planning':
            prompt=planning_other_prompt(goal,cat_list,additional_information,goal_int,error_info,behavior_from_library,behavior_from_library)
        elif agent_type=='Policy':
            prompt=policy_other_prompt(goal,cat_list,additional_information,goal_int,error_info,behavior_from_library)
        else:
            raise TransformationError("Unknown agent type.")
        system_prompt="I encountered this error while running the program. Please try to correct my mistake based on the syntax rules I provided."
        
    debugged_goal_int=ask_GPT(system_prompt,prompt)
    # print('=' * 80)
    print("Debugging finished.")
    print('=' * 80)
    return debugged_goal_int