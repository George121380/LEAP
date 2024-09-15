def Exp_helper_prompt(target_obj,discription):
    prompt="""
### Task Instruction ###
Based on the information, clearly tell the robot where it can find the target item.

### Target Object ###
""" + target_obj + """

### Information ###
""" + discription + """
"""
    return prompt