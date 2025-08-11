def Exp_helper_prompt(target_obj,discription):
    prompt="""
### Task Instruction ###
Based on the provided information, clearly instruct the robot on where to find the target item, emphasizing the surrounding objectsnear the target to aid in its identification and retrieval.

### Target Object ###
""" + target_obj + """

### Information ###
""" + discription + """
"""
    return prompt