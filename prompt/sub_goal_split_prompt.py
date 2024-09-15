def sub_goal_prompt(task):
    prompt="""
## Task Instruction ##
I need you to use human common sense to break down a long-term task into several subtasks. You can refer to my case study to accomplish this. I need your sub-goals to be fairly high-level, not too specific. You can generate up to 4 sub-goals at most, however If the task is simple, you can output only one or two sub-goals. And try to think step bt step.

## Long Term task ##
"""+task+"""

## Principle ##
Only split subtasks when the next step depends on the information obtained from the previous step.

## Background Knowledge ##
This task is to be executed in a complex household setting. Many items often have multiple instances, such as there might be multiple tables, drawers, sinks, and so on. However, not all instances are always relevant to the task. For example, when you want to wash the clothes in a basket, you need to understand that not every basket contains clothes—you need to find the one that does.

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
1. Find the ingredients for making salad.
2. Wash the ingredients for the salad, and for those that need to be cut, cut them accordingly.
3. Put all the prepared ingredients into a plate.

Example 3:
Long Term Task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought: To wash the plates and cups, you need to first find them in the sink. There may be more than one sink in the scene, so you need to find the one that contains plates and cups. Then, you need to wash them using the dishwasher. Finally, you need to put the plates and cups on the table in the kitchen.

Output:
1. Find the sink with plates and cups.
2. Wash the plates and cups using the dishwasher.
3. Put the plates and cups on the table in the kitchen.

Example 4:
Long Term Task: Go to the kitchen and turn on the microwave.

Chain of thought: Walking into a room and then searching for an object within the room is often a disjointed way of breaking down tasks in my task environment. A better way to decompose subtasks is to design the subtask directly as finding the object in the room.

Output:
1. Find the microwave in the kitchen.
2. Turn on the microwave in the kitchen.

Example 5:
Long Term Task: Make some potato chicken noodle, put it in a box, and store it in the fridge.

Output:
1. Clean and prepare the ingredients to make potato chicken noodle., 
2. Cook the potato chicken noodle., 
3. Put the potato chicken noodle in a box.,
4. Store the box in the fridge.

## Output Format ##
You only need to output several sub-goals with serial numbers, each line representing one sub-goal. Try to use the simplest and most straightforward language. Please do not provide any explanations or additional symbols.
"""
    return prompt