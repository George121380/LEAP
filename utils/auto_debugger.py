import re
from prompt.auto_debug_prompt import not_found_prompt,unknown_prompt,other_prompt
from concepts.dm.crow.parsers.cdl_parser import TransformationError
from Interpretation import ask_GPT
def auto_debug(error_info,original_content,goal_int,goal,additional_information,cat_list,goal_start_line_num):
    print('=' * 80)
    print("Debugging...")
    # print('=' * 80)
    # print("Error information: ",error_info)
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
    
    elif "at line" in error_info:
        error_line_num= int(re.search(r'at line (\d+)', error_info).group(1))
        error_line_num=error_line_num-goal_start_line_num
        useful_error_info=error_info.split('\n')[0]
        useful_error_info=re.sub(r'(at line )(\d+)', str(error_line_num), useful_error_info)
        prompt=other_prompt(goal,cat_list,additional_information,goal_int,useful_error_info)
        system_prompt="I encountered this error while running the program. Please try to correct my mistake based on the syntax rules I provided."
        

    else:
        prompt=other_prompt(goal,cat_list,additional_information,goal_int,error_info)
        system_prompt="I encountered this error while running the program. Please try to correct my mistake based on the syntax rules I provided."
        
    debugged_goal_int=ask_GPT(system_prompt,prompt)
    # print('=' * 80)
    print("Debugging finished.")
    print('=' * 80)
    return debugged_goal_int

def exploration_auto_debug(representation,cates):
    exp_test_file='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/exp_test.cdl'
    scene_file='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/init_scene.cdl'
    with open(scene_file, "r") as file:
        scene_info = file.read()
    instance_name=[]
    for cat in cates:
        instance_name.append(cat.replace('is_',''))
    test_cdl="behavior __goal__():\n"
    test_cdl+="  body:\n"
    idx=0
    for name,cate in zip(instance_name,cates):
        test_cdl+="    bind "+name+": item where:\n"
        test_cdl+="      "+cate+"("+name+")\n"
        test_cdl+="    achieve not unknown("+name+")\n"

    
    combined_content = scene_info + "\n" + representation+"\n"+test_cdl
    with open(exp_test_file, "w") as file:
        file.write(combined_content)