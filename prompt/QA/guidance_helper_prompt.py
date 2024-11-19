def Guidance_helper_prompt(task,guidance,task_info):
    Goal=task_info['Goal']
    Sub_goals=''
    for sub_goal in task_info['Subgoals']:
        Sub_goals+=sub_goal+'\n'
    prompt="""
### Instruction ###
A household robot is attempting to complete a task but has encountered some difficulties. It is seeking your guidance. Below are your thoughts on how to complete the task. Based on these thoughts, provide the robot with clear guidance. The guidance you provide must be a strict subset of the steps described in "Your Thoughts." You are not allowed to add extra details or elaborate beyond the given thoughts. The actions discussed here are relatively abstract, so avoid specifying exact amounts or durations (e.g., "how much" or "how long"). If the robot’s plan significantly deviates from your thoughts, you may suggest that the robot should replan.

### Task Information ###
Goal for the robot: """+Goal+""" 
Current subgoals planned by the robot: 
"""+Sub_goals+"""

### Robot's Question ###
"""+task+"""

### Your thought ###
To successfully complete the task, the robot should ideally follow these steps: """+guidance+"""

### Output Format ###
Need to replan: Yes/No
Guidance: [Your guidance]
"""

    return prompt