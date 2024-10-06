def sub_goal_prompt(task):
    prompt="""
## Task Instruction ##
Please break down a long-term task into several high-level sub-tasks using common sense. Refer to my case study as needed. Aim for up to 4 sub-tasks; if the task is simple, only 1 or 2 are necessary. And try to think step bt step.

## Long Term task ##
"""+task+"""

## Principle ##
Only split into subtasks when the next step relies on information obtained from a previous step. When the task is not very complex, reduce the number of subtasks as much as possible. And avoid setting sub-tasks such as gathering required items. A good task breakdown usually has one and only one clear and specific goal within a single sub-task.

## Tips ##
Creating a sub-task just for gathering related items is usually inefficient. It is better to find tools or objects as they become necessary during the task.

## Background Knowledge ##
This task occurs in a complex household environment, where items like tables, drawers, and sinks may have multiple instances. However, not all instances are always relevant to the task. For example, when you want to wash the clothes in a basket, you need to understand that not every basket contains clothes—you need to find the one that does.

## Examples ##
Example 1:
Long Term Task: Clean up the food on the table.

Chain of thought: Your long-term goal is to clean up the food on the table, but there are usually more than one table in the scene, so you need to identify the table with the food. Then, different types of food will have different suitable storage locations, but at this point, you don't know exactly what kinds of food are on the table, so you need to identify the types of food first. Finally, once you've confirmed the types of food on the table, you need to clean them up and store them in the appropriate places

Output:
1. Find a table with food on it.
2. Put the food in the appropriate storage locations.

Output Analysis:
The key to the first step is to find the table with the food on it, not to find a table and then check if there is food on it. If there is no food on the table, the task cannot proceed to the next step.

Example 2:
Long Term Task: Prepare a plate of salad.

Chain of thought: To make a salad, you typically need to start by finding and washing the ingredients. Next, you need to prepare these ingredients; for example, if you're adding kiwi, you'll usually need to cut it. Finally, you need to place all the prepared ingredients into a plate.

Output:
1. Wash the ingredients for the salad, and for those that need to be cut, cut them accordingly.
2. Put all the prepared ingredients into a plate.

Example 3:
Long Term Task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought: To wash the plates and cups, you need to first find them in the sink. There may be more than one sink in the scene, so you need to find the one that contains plates and cups. Then, you need to wash them using the dishwasher. Finally, you need to put the plates and cups on the table in the kitchen.

Output:
1. Find the sink with plates and cups.
2. Wash the plates and cups using the dishwasher.
3. Put the plates and cups on the table in the kitchen.

Example 4:
Long Term Task: Turn on the microwave.

Chain of thought: This task is relatively simple. You can directly find the microwave and turn it on.

Output:
1. Turn on the microwave.

Example 5:
Long Term Task: Make some potato chicken noodle, put it in a box, and store it in the fridge.

Output:
1. Clean and prepare the ingredients to make potato chicken noodle., 
2. Cook the potato chicken noodle., 
3. Put the potato chicken noodle in a box.,
4. Store the box in the fridge.

## Output Format ##
You only need to output several sub-tasks with serial numbers, each line representing one sub-tasks. Try to use the simplest and most straightforward language. Please do not provide any explanations or additional symbols.
"""
    return prompt