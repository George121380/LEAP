def sub_goal_prompt(overall_goal,completed_subgoal_list,human_guidance):

    completed_subgoals=''
    guidance=''
    if len(completed_subgoal_list) == 0:
        completed_subgoals = "No subgoals have been completed yet."
    else:
        for subgoal in completed_subgoal_list:
            completed_subgoals += f"- {subgoal} "


    if human_guidance == '':
        guidance = "No human guidance has been provided yet."
    else:
        guidance=human_guidance
    

    

    prompt=f"""
## Principle ##
When the task is not very complex, reduce the number of subtasks as much as possible. And avoid setting sub-tasks such as gathering required items. A good task breakdown usually has one and only one clear and specific goal within a single sub-task.

## Notes ##
- It is strictly prohibited to use a single subgoal solely for gathering related items, as this usually leads to ineffective task decomposition. In other words, please avoid designing subtasks like "Gather xxx" or "Collect xxx." or "Combine xxx". If you must gather certain items together, be sure to specify a clear "destination," meaning where exactly they should be collected, or a better approach is to integrate them into other subgoals.
- This task occurs in a complex household environment, where items like tables, drawers, and sinks may have multiple instances. However, not all instances are always relevant to the task. For example, when you want to wash the clothes in a basket, you need to understand that not every basket contains clothes—you need to find the one that does.

## Examples ##
Note: Chain of thought should not be included in the output.
Example 1:
Overall Goal: Clean up the food on the table.
Completed things: No subgoals have been completed yet.
Human Guidance: No human guidance has been provided yet.

Chain of thought: Your Overall Goal is to clean up the food on the table, but there are usually more than one table in the scene, so you need to identify the table with the food. Then, different types of food will have different suitable storage locations, but at this point, you don't know exactly what kinds of food are on the table, so you need to identify the types of food first. Finally, once you've confirmed the types of food on the table, you need to clean them up and store them in the appropriate places

Output:
1. Find a table with food on it.
2. Put the food in the appropriate storage locations.

Output Analysis:
The key to the first step is to find the table with the food on it, not to find a table and then check if there is food on it. If there is no food on the table, the task cannot proceed to the next step.

Example 2:
Overall Goal: Prepare a plate of salad.
Completed things: No subgoals have been completed yet.
Human Guidance: No human guidance has been provided yet.

Chain of thought: To make a salad, you typically need to start by finding and washing the ingredients. Next, you need to prepare these ingredients; for example, if you're adding kiwi, you'll usually need to cut it. Finally, you need to place all the prepared ingredients into a plate.

Output:
1. Wash the ingredients for the salad, and for those that need to be cut, cut them accordingly.
2. Put all the prepared ingredients into a plate.

Example 3:
Overall Goal: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.
Completed things: - Find the plates and cups. - Wash the plates and cups.
Human Guidance: There are more than one table in the scene, so please put it on the table in the kitchen.

Chain of thought: It is known that the plates and cups have already been identified and cleaned. Referring to the overall goal, the next step is simply to place the plates and cups on the table in the kitchen. This process is not complicated, and there is no need to further divide the task at this point. Therefore, you can directly proceed with the next step, but be sure to follow the human instructions: the next goal must emphasize placing the items on the kitchen table, not any other table.

Output:
No decomposition: Put the plates and cups on the table in the kitchen.

Example 4:
Overall Goal: Turn on the microwave.
Completed things: No subgoals have been completed yet.
Human Guidance: No human guidance has been provided yet.

Chain of thought: This task is relatively simple. You can directly find the microwave and turn it on.

Output:
No decomposition: Turn on the microwave.

Example 5:
Overall Goal: Make some potato chicken noodle, put it in a bowl, and store it in the fridge.
Completed things: - Clean the potato and the chicken.
Human Guidance: To cook potato chicken noodle, you need to boil noodles, chicken, and potato one by one.

Chain of thought: The overall goal is to make potato chicken noodle, put it in a bowl, and store it in the fridge. And the ingredients have been cleaned. The next step is to cook the potato chicken noodle. The human guidance provides the specific steps to cook the potato chicken noodle, so you can directly proceed with the next step. After cooking, you can put the potato chicken noodle in a bowl and store it in the fridge.

Output:
1. Boil the noodles, chicken, and potato one by one.
2. Put the potato chicken noodle in a bowl.
3. Store the bowl in the fridge.

Example 5:
Overall Goal: Roast Chicken.
Completed things: - Clean the chicken.
Human Guidance: I don't want to add any seasoning. Just put it into a oven to roast.

Chain of thought: The human guidance indicates that the chicken should be roasted without any seasoning. The chicken has been cleaned, so the next step is to put the chicken into the oven to roast. This task is relatively simple and does not require further decomposition.

Output:
No decomposition: Put the chicken into the oven to roast.

## Output Format ##
When you think the next task is simple and doesn't require decomposition, make sure your output starts with the keyword "No decomposition:", followed by the next goal on the same line. When the next goal is complex and requires decomposition, output the following subgoals in separate lines with numbered steps. Try to use the simplest and most direct language. Please do not include any explanations or special symbols in your output.

## Current task informatioin ##
Overall Goal: {overall_goal}
Completed things: {completed_subgoals}
Human Guidance: {guidance}
"""
    return prompt