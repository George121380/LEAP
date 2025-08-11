import sys
sys.path.append('..')
sys.path.append('../utils')
from action_explaination import controller_to_natural_language

def sub_goal_evaluate_prompt(goal_representation,action_history,current_subgoal,full_goal, next_subgoal,collected_information,obj_list):
    actions=''
    if action_history!=None:
        for id in range(len(action_history)):
            actions+=f'action{id+1}: '+controller_to_natural_language(action_history[id]['action'])+'-> effect: '+action_history[id]['effects']+'\n'
    objs=''
    for obj in list(obj_list):
        objs+=str(obj)+'\n' 
    prompt="""
### Task Overview ###
Evaluate whether the current sub-task is complete by reviewing the actions performed and the information provided. Focus on verifying that all necessary items are present, assuming their conditions and locations are correct. Confirm that the goals defined in the goal representation have been achieved, with the assumption that all mentioned actions have been successfully executed. A goal should be marked as complete once any action associated with it is detected (e.g., turning a faucet on or off indicates that the task of filling water has been completed).

### Guidance ###
- Assume all actions listed under 'Actions Taken' have been successfully executed without error.
- You do not need to account for physical constraints such as object size, space availability, or task execution issues (e.g., whether there is sufficient space). Assume that all such physical conditions are perfectly resolved. Focus solely on whether the logical goals have been met based on the provided actions and information.
- You don't need to worry about the execution time of actions; we assume that all actions achieve the desired effect immediately after execution. Common misjudgments include: worry about whether food is properly cooked, or whether a container is filled
- The length of the 'Actions Taken' list does not directly indicate task completion. A short list does not mean the sub-task is incomplete, nor does a long list guarantee completion. Use all provided information to make your evaluation.
- The robot's possible actions are limited to the following: walk, switch off, switch on, put, put in, grab, wash, scrub, rinse, open, close, plug in, plug out, cut, wipe, touch, type, push, and pull. Complex actions such as "cook" or "wait" are not included in our problem formulation. Therefore, you should neither expect nor require the robot to perform actions beyond those listed above.

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
    