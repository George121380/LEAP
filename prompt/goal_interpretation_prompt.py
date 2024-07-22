def get_goal_inter_prompt(goal,cat_list=None,additional_information=None):
    if additional_information==None:
        additional_information="None"
    categories=""
    for cat in cat_list:
        categories+="- is_"+cat+"(x: item)\n"
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""
## Task Instructions:
You need to analyze the goal and additional information that I provide(sometimes there may be no additional information), refer to the example, and transform them into the formal representation defined below. Your output may include several behaviors. In the body section of each behavior, you need to declare some intermediate states, intermediate relationships, final states, and final relationships required to achieve the goal. You do not need to provide the actions needed to achieve the goal. Once you provide the intermediate states, intermediate relationships, final states, and final relationships, my algorithm will plan a feasible sequence of actions on its own. Please note that the states, relationships, properties, and keywords you use must not exceed the scope I provided. Please check this carefully before outputting, otherwise the program will not run. Additionally, behavior __goal__(): is a required structure, functioning similarly to the main function in Python.

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
- close_item(x: item, y: item)
- close(x: character, y: item)
- facing(x: item, y: item)
- holds_rh(x: character, y: item)
- holds_lh(x: character, y: item)

## available category determination:
"""+categories+"""
For any instance x:item, you can use is_y(x) to determine if x belongs to category y. You cannot perform any operations on a category; you can only determine the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use:
bind b: item where:
    is_box(b)

## Syntax rules and keywords:
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
You can only output the description of the converted goal and additional information. Do not include any explanation or any other symbols.

"""
    return prompt