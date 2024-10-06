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
Assess whether the current sub-task is complete by reviewing the actions taken and the information gathered. Focus on whether all necessary items are present, assuming their locations and conditions are correct. Confirm if the goals outlined in the goal representation have been achieved, as all mentioned actions are assumed executed correctly. A goal can be marked as complete as soon as a corresponding action occurs (e.g., turning a faucet on or off indicates water has been filled).

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
    