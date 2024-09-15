import sys
sys.path.append('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/utils')
from action_explaination import controller_to_natural_language

def sub_goal_evaluate_prompt(goal_representation,action_history,current_subgoal,full_goal, next_subgoal,collected_information,obj_list):
    actions=''

    for id in range(len(action_history)):
        actions+=f'action{id+1}: '+controller_to_natural_language(action_history[id]['action'])+'-> effect: '+action_history[id]['effects']+'\n'
    objs=''
    for obj in list(obj_list):
        objs+=str(obj)+'\n' 
    prompt="""
### Task Overview ###
Evaluate whether the current sub-task has been completed by reviewing the actions taken and the information collected. Determine if the sub-task is complete and assess readiness to proceed to the next sub-task. Generally, you only need to check if all the necessary items for the task are present; their location and condition are usually correct. And the content in goal representation is achieved already. And you can assume all the actions mentioned below are executed correctly.

### Current Sub-Task ###
"""+current_subgoal+"""

### Actions Taken ###
"""+actions+"""

### Information Collected ###
"""+collected_information+"""

### Next Sub-Task ###
"""+next_subgoal+"""

### Full Goal ###
"""+full_goal+"""

### Goal Representation ###
"""+goal_representation+"""

### Output Format ###
Please provide your evaluation in the following format:
- Sub-Task Completed: Yes/No
- Next Steps: If "Yes", summarize clearly and concisely in second-person ("you") what the robot did in this sub-task. If "No", clearly and concisely point out what else needs to be done, without over-explaining.
"""
    return prompt
    