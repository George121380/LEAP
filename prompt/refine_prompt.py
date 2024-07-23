def refine_prompt(goal,cat_list=None,additional_information=None,goal_representation=None):
    if additional_information==None:
        additional_information="None"
    categories=""
    for cat in cat_list:
        categories+="- is_"+cat+"(x: item)\n"
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""

## Task Instructions:
I need you to check and correct the goal representations I have made below, one by one, according to the checklist based on the goals and additional information.

## The goal representations are:
""" + goal_representation + """

## Checklist:
1.Check if the goal representations use any states, relationships, categories, or keywords outside the specified range. If there are any, please correct them to the closest representation within the specified range.
2.Check if all functions called in the goal have been declared, ensuring that no undefined or undeclared functions are called. If there are any, please add the undeclared functions.
3.Check if the syntax used in the goal representations conforms to the definitions in the Syntax rules and keywords. If there are any errors, please help me correct them.
4.Check if each variable is declared before use.
5.Check if the character in the body is written as char as required.

## The available states are:
- is_on(x: item)
- is_off(x: item)
- plugged(x: item)
- unplugged(x: item)
- open(x: item)
- closed(x: item)
- dirty(x: item)
- clean(x: item)
- sitting(x: character)
- lying(x: character)

## The available relationships are:
- on(x: item, y: item)
- on_char(x: character, y: item)
- inside(x: item, y: item)
- inside_char(x: character, y: item)
- between(door: item, room: item)
- close(x: item, y: item)
- close_char(x: character, y: item)
- facing(x: item, y: item)
- facing_char(x: character, y: item)
- holds_rh(x: character, y: item)
- holds_lh(x: character, y: item)
Here are a few easily confusing usages to note:
In relationships with the _char suffix, the first parameter must always be a char. For example, on and on_char, inside and inside_char, close and close_char, facing and facing_char.


## available category determination:
"""+categories+"""
For any instance x:item, you can use is_y(x) to determine if x belongs to category y. You cannot perform any operations on a category; you can only determine the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use:
bind b: item where:
    is_box(b)

## Syntax rules and keywords:
Please use "char" to represent character.

Following are all the keywords that you can use to convert the information into a structured format, Please ensure that you do not use any keywords other than these.

# bind
# Usage: Select any item that meets the conditions and assign it to the specified variable.
bind x: item where:
    is_light(x)

# foreach
# Usage: Iterates over all objects of a certain type.
foreach o: item:
    achieve closed(o)

# exist
# Usage: Checks if a variable with a certain property exists.
exist p: item : is_on(p)

# behavior
# Usage: Defines a behavior rule.
behavior turn_off_light(light:item):
goal: is_off(light)
body:
    achieve is_on(light)

# goal
# Usage: Specifies the goal condition for a behavior.
goal: clean(o)

# body
# Usage: Contains the sequence of actions and subgoals to achieve the behavior’s goal.
body:
    achieve close(a)
    achieve clean(b)

# if-else
# Usage: Conditional statement for branching logic.
if condition:
    achieve close(a)
else:
    achieve clean(b)

# unordered
# Usage: When the execution order may affect the success of the task and the order cannot be determined in advance, you can use this keyword to allow the program to decide the execution order by itself. This can increase the success rate of complex tasks, but it will also incur higher computational costs.
body:
    unordered:
        achieve close(a)
        achieve clean(b)

## Example-1:

When the goal is: 
Find the groceries and carry them into the kitchen. Place them on the counter and begin to sort them out. Place the vegetables, eggs, cheese, and milk in the fridge.

The additional information is: None

The output is:
behavior __goal__():
    body:
        bind fridge: item where:
            is_fridge(fridge)
        foreach o: item:
            if is_vegetable(o) or is_egg(o) or is_cheese(o) or is_milk(o):
                achieve inside(o, fridge)

Example Analysis: To achieve the goal, we must first ensure there is a refrigerator in the environment. However, we don't need to specify which refrigerator, so we use the keyword bind to select any refrigerator. Next, we need to place the vegetables, eggs, cheese, and milk into the refrigerator. The "foreach" keyword ensures that all items categorized as vegetables, eggs, cheese, and milk are eventually in the refrigerator.
          
# Example-2:
When the goal is:
Clean all the plates and cups with dishwasher. Then put them on the table.

The additional information is:
- Dishwasher is a good way to clean plates and cups.
- The dishwasher must be closed and turned on to start the cleaning process.

The output is:
behavior clean_all_plates_and_cups_by_dishwasher():
    body:
        bind dishwasher: item where:
            is_dishwasher(dishwasher)
        foreach o: item:
            if is_plate(o) or is_cup(o):
                achieve inside(o, dishwasher)
        achieve closed(dishwasher)
        achieve is_on(dishwasher)

behavior put_all_plates_and_cups_on_table():
    body:
        bind table: item where:
            is_table(table)
        foreach o: item:
        if is_plate(o) or is_cup(o):
            achieve on(o, table)

behavior __goal__():
    body:
        clean_all_plates_and_cups()
        put_all_plates_and_cups_on_table()
    

Example Analysis: 
Completing this goal involves two stages: washing dishes and cups with a dishwasher, then put them on the table. First, all the dishes and cups need to be placed into the dishwasher, then the dishwasher must be closed and started. After washing, the dishes and cups need to be placed on the dining table.

# Example-3:
When the goal is:
Close all the doors

The additional information is: None

The output is:
behavior close_all_doors():
    body:
        unordered:
            foreach o: item:
                if is_door(o):
                    achieve close(o)

Example Analysis: 
This case aims to demonstrate the use of 'unordered' because to close a door, you must be close to it. When closing multiple doors, the order is very important. If you close the wrong door, it might block the path to another door. In such a case, you would have to reopen the already closed door to reach the other one, which might lead to the failure of the task. Therefore, the 'unordered' keyword is used here to automatically find the appropriate execution order.

## Output Format:
Only output the corrected goal representations. Do not add any explanations, comments, or other additional symbols; otherwise, the program will be considered incorrect.
"""
    return prompt