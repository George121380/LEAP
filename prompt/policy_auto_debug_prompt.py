def policy_not_found_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None):
    #using a name that is not in the available categories
    if additional_information==None:
        additional_information="None"
    categories=""
    for cat in cat_list:
        categories+="- is_"+cat+"(x: item)\n"
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""

## Task Instructions:
I am converting my goals and additional information into a formal representation. Currently, my formal representation contains undefined category names. Please correct the errors in the formal representation based on the error messages.
Prioritize using synonyms to replace the undefined category names. If that's not possible, use categories with similar functions. However, under all circumstances, ensure that the corrected item categories appear in the available categories. I will demonstrate how to make replacements in the example section.

## Formal Representation:
""" + goal_representation + """

## Error:
The formal representation include such undefined categories: """+error_info+"""
Please refer to the 'Available Category Determination' below to make modifications here.

## Available Category Determination:
"""+categories+"""
For any instance 'x', you can use 'is_y(x)' to determine if 'x' belongs to category 'y'. Categories cannot be operated upon directly; you can only assess the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use the following syntax:

bind b: item where:
    is_box(b)

Important Notes:
If the category you need is not in the available list, try to find a synonym or a similar category with a closely related function.

## Example:
- is_food(0) -> is_food_food(), Although the first type of translation is intuitive, when is_food is not in the available category, but is_food_food is. These two have similar meanings, so such a replacement should be made.
- is_soapy_water() -> is_cleaning_solution(), soapy water is not an available category, but cleaning solution is. They are functionally similar, so such a replacement should be made.

## Output Format:
Only replace the incorrect category names without modifying any other parts, including content and indentation. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt

def policy_unknown_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None,behavior_from_library=None):
    if additional_information==None:
        additional_information="None"
    categories=""
    for cat in cat_list:
        categories+="- is_"+cat+"(x: item)\n"
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""

## Task Instructions:
I am converting my goals and additional information into a formal representation. Currently, my formal representation contains undefined vairable names. Please correct the errors in the formal representation based on the error messages.
An instance variable is used in the behavior without prior declaration and definition. One case is when a parameter used in the goal of the behavior is not declared in the behavior's parameters. Another case is when a variable name used in the body of the behavior is not declared using methods such as bind or foreach. For these situations, refer to the examples I provided for making modifications.

## The goal representations are:
""" + goal_representation + """

## error:
In the goal representation, this variable is not defined: """+error_info+""". Please refer to the example below to supplement the declaration of this variable.

## Available States:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- is_on(x: item) # The item is turned on.
- is_off(x: item) # The item is turned off.
- plugged(x: item) # The item is plugged in.
- unplugged(x: item) # The item is unplugged.
- open(x: item) # The item is open.
- closed(x: item) # The item is closed.
- dirty(x: item) # The item is dirty.
- clean(x: item) # The item is clean.
- has_water(x: item) # The item has water inside or on it.
- cut(x: item) # The item is cut.
- inhand(x: item) # A item is grasped by a character. Only use it when an item needs to be continuously held in your hand.
- has_a_free_hand(x: character) # The character has a free hand.
- visited(x: item) # The character has observed the item
Important Note: Please note that you can take at most two items. Having too many items in hand will result in no solution.

## Available Relationships:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- on(x: item, y: item) # item x is on top of item y
- inside(x: item, y: item) # item x is inside item y, and y should be a room or a container
- inside_char(x: character, y: item) # character is inside item y (Character is you self. Any other animal like cat is an item)
- close(x: item, y: item) # item x is close to item y
- close_char(x: character, y: item) # character is close to item y (Character is you self. Any other animal like cat is an item)
- facing(x: item, y: item) # item x is facing item y
- facing_char(x: character, y: item) # character is facing item y (Character is you self. Any other animal like cat is an item)
Important Usage Notes: In relationships with the '_char' suffix, the first parameter must always be a char. For example, 'inside' and 'inside_char', 'close' and 'close_char', 'facing' and 'facing_char'.

## Available Properties:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
- surfaces(x: item) #  Indicates that the item has a surface where things can be placed, such as a kitchen countertop or table.
- grabbable(x: item) # Indicates that the item can be grabbed by hand.
- hangable(x: item) # Indicates that the item can be hung on.
- drinkable(x: item) # Indicates that the item can be drunk.
- eatable(x: item) # Indicates that the item can be eaten.
- recipient(x: item) # Indicates that the item can receive something.
- cuttable(x: item) # Indicates that the item can be cut with a knife.
- pourable(x: item) # Indicates that the item can be poured into another container or onto other items.
- can_open(x: item) # Indicates that the item can be opened.
- has_switch(x: item) # Indicates that the item has a switch to turn it on or off.
- readable(x: item) # Indicates that the item can be read.
- lookable(x: item) # Indicates that the item can be looked at.
- containers(x: item) # Indicates that the item is a container.
- body_part(x: item) # Indicates that the item is a body part.
- cover_object(x: item)
- has_plug(x: item) # Indicates that the item has a plug.
- movable(x: item) # Indicates that the item can be moved.
- cream(x: item) # Indicates that the item is a cream.
- is_clothes(x: item) # Indicates that the item is clothing.
- is_food(x: item) # Indicates that the item is food.
Important Notes: "propertie" cannot be assigned a value; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions.
Common Errors:
has_plug(lamp) = True # Incorrect. You cannot assign a value to a property, as they are immutable.

# Available Behaviors:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
The following behaviors can be directly invoked in the current sub-task goal representation, with parameters passed in like function arguments.
- observe(obj:item,question:string) # observe is a special behavior used to inspect an object. You can specify the purpose of your inspection with a string. By calling observe, you can learn about the state of an object as well as its relationship with surrounding objects. After observing an item, it will be marked as visited. Note that the second parameter of observe is a string and must be enclosed in double quotes("").
- put_close(inhand_obj: item, obj: item) # Put an item close to another item, this behavior will make close(inhand_obj, obj) true.
- put_on(inhand_obj: item, obj: item) # Put an item on another item, this behavior will make on(inhand_obj, obj) true.
- put_inside(inhand_obj: item, obj: item) # Put an item inside another item, this behavior will make inside(inhand_obj, obj) true.
- walk_to(obj: item) # Get close to an object, this behavior will make close_char(char, obj) true.
- switch_on(obj: item) # Switch on an item, this behavior will make is_on(obj) true.
- switch_off(obj: item) # Switch off an item, this behavior will make is_off(obj) true.
- opens(obj: item) # Open an item, this behavior will make open(obj) true.
- closes(obj: item) # Close an item, this behavior will make closed(obj) true.
- plugin(obj: item) # Plug in an item, this behavior will make plugged(obj) true.
- plugout(obj: item) # Plug out an item, this behavior will make unplugged(obj) true.
- grab(obj: item) # Grab an item, this behavior will make inhand(obj) true.
- cuts(obj: item) # Cut an item, this behavior will make cut(obj) true.
- wipe(obj: item) # Wipe an item, this behavior will make clean(obj) true.
- get_water(obj: item) # Get water, this behavior will make has_water(obj) true.
- empty_a_hand() # Empty a hand, this behavior will make has_a_free_hand(char) true, and release the item in hand.
- wash(obj:item) # Wash an item by hand, this behavior can make obj clean.
- scrub(obj:item) # Scrub an item, this behavior can make obj clean.
- rinse(obj:item) # Rinse an item, this behavior can make obj clean.
- squeeze(obj:item) # Squeeze an item.
- move(obj:item) # Move an item.
- pull(obj:item) # Pull an item.
- push(obj:item) # Push an item.
- look_at(obj:item) # Look at an item.
- drink(obj: item) # Drink an item.
- watch(obj:item) # Watch an item.
- type(obj:item) # Type on an item.
- touch(obj:item) # Touch an item.
- read(obj:item) # Read an item.
- water(obj:item) # Fill item with water.
Important Note: Ensure that all parameters are properly defined before using them in the behaviors.

"""+behavior_from_library+"""
## Available Category Determination:
"""+categories+"""
For any instance 'x', you can use 'is_y(x)' to determine if 'x' belongs to category 'y'. Categories cannot be operated upon directly; you can only assess the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use the following syntax:

bind b: item where:
    is_box(b)

Important Notes:
If the category you need is not in the available list, try to find a synonym or a similar category with a closely related function.
Examples:
- food -> is_food_food(): If 'is_food' is not available, but 'is_food_food' is, use the latter as they have similar meanings.
- soapy_water -> is_cleaning_solution(): If 'soapy_water' is not available, but 'cleaning_solution' is, use the latter as they are functionally similar.

## Syntax Rules and Keywords:
"char" is a constant instance representing a character (yourself) and we assume that other animals like cat is an item. The type "character" can only be used when defining an instance. Use "char" consistently when passing parameters, and use "character" when defining a variable and specifying its type.

Below are all the keywords you can use to convert information into a structured format. Please ensure that you do not use any keywords other than those listed here.

Keywords:
# bind
# Usage: Randomly select an item that satisfies the specified conditions and assign it to a variable. If no item meets the condition, the program will fail. Therefore, avoid setting overly strict conditions unless you are certain that a corresponding item exists. The condition is_x will always be satisfied as long as x is specified in Available Category Determination. However, exercise caution when adding additional conditions.To maintain consistency, try to use 'bind' primarily in the '__goal__' behavior and pass the retrieved instances as parameters to invoked behaviors. Avoid using 'bind' in other behaviors whenever possible.
Example:
bind x: item where:
    is_light(x)

Multiple Items Example: Ensure that subsequent items are not the same as those previously bound.
bind apple1: item where:
    is_apple(apple1)
bind apple2: item where:
    is_apple(apple2) and apple1!=apple2
bind apple3: item where:
    is_apple(apple3) and apple1!=apple3 and apple2!=apple3

# foreach
# Usage: Iterates over all objects. Do not use 'where' in a 'foreach' statement. Additionally, do not nest one foreach inside another, as this will cause the program to fail.
Correct example:
foreach o: item:
    if can_open(o) and is_box(o):
        closes(o)

Incorrect example:
foreach o: item where:
    if can_open(o) and is_box(o):
        closes(o)

# behavior
# Usage: Defines a behavior rule. The keyword 'body' must appear in the behavior.

# body
# Usage: You can use logical statements and call other behaviors in 'body'.

# if-else
# Usage: Conditional statement for branching logic.
if condition:
    closes(a)
else:
    wash(b)

# exists
# Usage: Checks if there is at least one object that meets the condition and returns a boolean value.
Template: exists obj_name: objtype : condition()
Example: exists item1: item : holds_lh(char, item1)

# symbol
# Usage: Defines a symbol and binds it to the output of an expression. You can only use the symbol in the following manner:
symbol l=exists item1: item : (holds_lh(char, item1))

# def
# Usage: Defines a function that can be used to check a condition. 

## Example:
Please refer to the method used in the example below to modify the goal representation I provided in this round, supplementing the missing definitions and declarations. Each example below will provide both wrong and correct versions, so you can learn how I make the modifications.

- Wrong Version(light in make_dinner is not defined):
behavior make_dinner():
    body:
        switch_on(light)

-> corrected version:
behavior make_dinner(light:item):
    body:
        switch_on(light)
    
In this example, the original version of the behavior definition contains an undefined variable light in behavior "make_dinner". To correct this, I added the parameter light:item to the behavior definition.

- Wrong Version(obj1 and obj2 in obj_inside_or_on are not defined before use):
def obj_inside_or_on():
  return inside(obj1, obj2) or on(obj2, obj1)

-> corrected version:
def obj_inside_or_on(obj1: item, obj2: item):
  return inside(obj1, obj2) or on(obj2, obj1)

In this example, the original version of the function contains two undefined variables obj1 and obj2 in function obj_inside_or_on. To correct this, I added the parameters obj1: item and obj2: item to the function definition.

- Wrong Version(inhand_obj and obj in "goal" of put_close are not defined):
behavior put_close():
  goal: close(inhand_obj, obj)
  body:
    put(inhand_obj, obj)

-> corrected version:
behavior put_close(inhand_obj: item, obj: item):
  goal: close(inhand_obj, obj)
  body:
    put(inhand_obj, obj)

In this example, the original version of the goal definition contains two undefined variables inhand_obj and obj. To correct this, I added the parameters inhand_obj: item and obj: item in the behavior defination.

- Wrong Version("location" in "body" of drop is not defined):
behavior drop_to_somewhere(inhand_obj:item):
  goal: not inhand(inhand_obj)
  body:
    put(inhand_obj, location)

-> corrected version:
behavior drop(inhand_obj:item, location:item):
  goal: not inhand(inhand_obj)
  body:
    put(inhand_obj, location)

In this example, the original version of the behavior definition contains an undefined variable location in the body of the behavior "drop". To correct this, I added the bind statement to define the variable location.

Please note that, you can not provide any parameters to __goal__().
At the same time, please note that when you modify the parameters of a function or behavior, don't forget to also modify the function or behavior call statements to add any missing parameters.

## Output Format:
Output the goal representation with the supplemented definitions and declarations. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt

def policy_other_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None,behavior_from_library=None):
    if additional_information==None:
        additional_information="None"
    categories=""
    for cat in cat_list:
        categories+="- is_"+cat+"(x: item)\n"
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""

## Task Instructions:
My program is currently encountering an error. Please refer to the error message and the syntax rules I provided to correct this error.

## The goal representations are:
""" + goal_representation + """

## error:
"""+error_info+"""

## Precautions:
- Ensure that the states, relationships, properties, and keywords used do not exceed the scope I provided. (Available states, relationships, properties, and keywords are listed below.)
- If you invoke a function, ensure it’s properly defined, and include any necessary parameters when calling it.
- The behavior __goal__(): is required and functions similarly to the main function in Python; it should typically be placed at the end of your output without any parameters.

## Available States:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- is_on(x: item) # The item is turned on.
- is_off(x: item) # The item is turned off.
- plugged(x: item) # The item is plugged in.
- unplugged(x: item) # The item is unplugged.
- open(x: item) # The item is open.
- closed(x: item) # The item is closed.
- dirty(x: item) # The item is dirty.
- clean(x: item) # The item is clean.
- has_water(x: item) # The item has water inside or on it.
- cut(x: item) # The item is cut.
- inhand(x: item) # A item is grasped by a character. Only use it when an item needs to be continuously held in your hand.
- has_a_free_hand(x: character) # The character has a free hand.
- visited(x: item) # The character has observed the item
Important Note: Please note that you can take at most two items. Having too many items in hand will result in no solution.

## Available Relationships:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- on(x: item, y: item) # item x is on top of item y
- inside(x: item, y: item) # item x is inside item y, and y should be a room or a container
- inside_char(x: character, y: item) # character is inside item y (Character is you self. Any other animal like cat is an item)
- close(x: item, y: item) # item x is close to item y
- close_char(x: character, y: item) # character is close to item y (Character is you self. Any other animal like cat is an item)
- facing(x: item, y: item) # item x is facing item y
- facing_char(x: character, y: item) # character is facing item y (Character is you self. Any other animal like cat is an item)
Important Usage Notes: In relationships with the '_char' suffix, the first parameter must always be a char. For example, 'inside' and 'inside_char', 'close' and 'close_char', 'facing' and 'facing_char'.

## Available Properties:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
- surfaces(x: item) #  Indicates that the item has a surface where things can be placed, such as a kitchen countertop or table.
- grabbable(x: item) # Indicates that the item can be grabbed by hand.
- hangable(x: item) # Indicates that the item can be hung on.
- drinkable(x: item) # Indicates that the item can be drunk.
- eatable(x: item) # Indicates that the item can be eaten.
- recipient(x: item) # Indicates that the item can receive something.
- cuttable(x: item) # Indicates that the item can be cut with a knife.
- pourable(x: item) # Indicates that the item can be poured into another container or onto other items.
- can_open(x: item) # Indicates that the item can be opened.
- has_switch(x: item) # Indicates that the item has a switch to turn it on or off.
- readable(x: item) # Indicates that the item can be read.
- lookable(x: item) # Indicates that the item can be looked at.
- containers(x: item) # Indicates that the item is a container.
- has_plug(x: item) # Indicates that the item has a plug.
- movable(x: item) # Indicates that the item can be moved.
- is_clothes(x: item) # Indicates that the item is clothing.
- is_food(x: item) # Indicates that the item is food.
Important Notes: "propertie" cannot be assigned a value; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions.
Common Errors:
has_plug(lamp) = True # Incorrect. You cannot assign a value to a property, as they are immutable.

# Available Behaviors:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
The following behaviors can be directly invoked in the current sub-task goal representation, with parameters passed in like function arguments.
- observe(obj:item,question:string) # observe is a special behavior used to inspect an object. You can specify the purpose of your inspection with a string. By calling observe, you can learn about the state of an object as well as its relationship with surrounding objects. After observing an item, it will be marked as visited. Note that the second parameter of observe is a string and must be enclosed in double quotes("").
- put_close(inhand_obj: item, obj: item) # Put an item close to another item, this behavior will make close(inhand_obj, obj) true.
- put_on(inhand_obj: item, obj: item) # Put an item on another item, this behavior will make on(inhand_obj, obj) true.
- put_inside(inhand_obj: item, obj: item) # Put an item inside another item, this behavior will make inside(inhand_obj, obj) true.
- walk_to(obj: item) # Get close to an object, this behavior will make close_char(char, obj) true.
- switch_on(obj: item) # Switch on an item, this behavior will make is_on(obj) true.
- switch_off(obj: item) # Switch off an item, this behavior will make is_off(obj) true.
- opens(obj: item) # Open an item, this behavior will make open(obj) true.
- closes(obj: item) # Close an item, this behavior will make closed(obj) true.
- plugin(obj: item) # Plug in an item, this behavior will make plugged(obj) true.
- plugout(obj: item) # Plug out an item, this behavior will make unplugged(obj) true.
- grab(obj: item) # Grab an item, this behavior will make inhand(obj) true.
- cuts(obj: item) # Cut an item, this behavior will make cut(obj) true.
- wipe(obj: item) # Wipe an item, this behavior will make clean(obj) true.
- get_water(obj: item) # Get water, this behavior will make has_water(obj) true.
- empty_a_hand() # Empty a hand, this behavior will make has_a_free_hand(char) true, and release the item in hand.
- wash(obj:item) # Wash an item by hand, this behavior can make obj clean.
- scrub(obj:item) # Scrub an item, this behavior can make obj clean.
- rinse(obj:item) # Rinse an item, this behavior can make obj clean.
- squeeze(obj:item) # Squeeze an item.
- move(obj:item) # Move an item.
- pull(obj:item) # Pull an item.
- push(obj:item) # Push an item.
- look_at(obj:item) # Look at an item.
- drink(obj: item) # Drink an item.
- watch(obj:item) # Watch an item.
- type(obj:item) # Type on an item.
- touch(obj:item) # Touch an item.
- read(obj:item) # Read an item.
- water(obj:item) # Fill item with water.
Important Note: Ensure that all parameters are properly defined before using them in the behaviors.

"""+behavior_from_library+"""
## Available Category Determination:
"""+categories+"""
For any instance 'x', you can use 'is_y(x)' to determine if 'x' belongs to category 'y'. Categories cannot be operated upon directly; you can only assess the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use the following syntax:

bind b: item where:
    is_box(b)

Important Notes:
If the category you need is not in the available list, try to find a synonym or a similar category with a closely related function.
Examples:
- food -> is_food_food(): If 'is_food' is not available, but 'is_food_food' is, use the latter as they have similar meanings.
- soapy_water -> is_cleaning_solution(): If 'soapy_water' is not available, but 'cleaning_solution' is, use the latter as they are functionally similar.

## Syntax Rules and Keywords:
"char" is a constant instance representing a character (yourself) and we assume that other animals like cat is an item. The type "character" can only be used when defining an instance. Use "char" consistently when passing parameters, and use "character" when defining a variable and specifying its type.

Below are all the keywords you can use to convert information into a structured format. Please ensure that you do not use any keywords other than those listed here.

Keywords:
# bind
# Usage: Randomly select an item that satisfies the specified conditions and assign it to a variable. If no item meets the condition, the program will fail. Therefore, avoid setting overly strict conditions unless you are certain that a corresponding item exists. The condition is_x will always be satisfied as long as x is specified in Available Category Determination. However, exercise caution when adding additional conditions.To maintain consistency, try to use 'bind' primarily in the '__goal__' behavior and pass the retrieved instances as parameters to invoked behaviors. Avoid using 'bind' in other behaviors whenever possible.
Example:
bind x: item where:
    is_light(x)

Multiple Items Example: Ensure that subsequent items are not the same as those previously bound.
bind apple1: item where:
    is_apple(apple1)
bind apple2: item where:
    is_apple(apple2) and apple1!=apple2
bind apple3: item where:
    is_apple(apple3) and apple1!=apple3 and apple2!=apple3

# foreach
# Usage: Iterates over all objects. Do not use 'where' in a 'foreach' statement. Additionally, do not nest one foreach inside another, as this will cause the program to fail.
Correct example:
foreach o: item:
    if can_open(o) and is_box(o):
        closes(o)

Incorrect example:
foreach o: item where:
    if can_open(o) and is_box(o):
        closes(o)

# behavior
# Usage: Defines a behavior rule. The keyword 'body' must appear in the behavior.

# body
# Usage: You can use logical statements and call other behaviors in 'body'.

# if-else
# Usage: Conditional statement for branching logic.
if condition:
    closes(a)
else:
    wash(b)

# exists
# Usage: Checks if there is at least one object that meets the condition and returns a boolean value.
Template: exists obj_name: objtype : condition()
Example: exists item1: item : holds_lh(char, item1)

# symbol
# Usage: Defines a symbol and binds it to the output of an expression. You can only use the symbol in the following manner:
symbol l=exists item1: item : (holds_lh(char, item1))

# def
# Usage: Defines a function that can be used to check a condition. 

## Background Knowledge:
In general, you only know part of the information in a given scenario. For example, you might know that a certain piece of clothing is in a particular basket, but you might not know what is in a certain basket. Therefore, many times, you need to first perform a goal conversion based on what you already know. When you lack some information, you can observe and obtain the information you want by using obs(target_item, information).
For example,if you want to know if there any clothes in the basket_34, you can use:
bind basket: item where:
    is_basket(basket) and id[basket]==34
observe(basket,"Check is there any clothes in the basket")

If you want to know Is there any trash in the trash can in the dining room, you can use:
def in_the_dining_room(trash_can:item):
    symbol in_dining_room=exists room: item : (is_dining_room(room) and inside(trash_can, room))
    return in_dining_room

bind trash_can: item where:
    is_trash_can(trash_can) and in_the_dining_room(trash_can) # Since you already know that the trash can is located in the dining room, you can include the condition inside(trash_can, dining_room). However, if the location of the trash can is unknown, this condition must be omitted.
observe(trash_can,"Check is there any trash in the trash can")

## Examples:
## Example-1-1:
Current sub-task goal: 1. Find a table with food.
The completed sub-tasks: None, it is the first sub-task.
Additional information: None.
Long-horizon task: Clean up the food on the table.
Chain of thought: Your current sub-task goal is to find a table with food on it, which is the first step towards completing the long-horizon task: "Clean up the food on the table."
According to the background knowledge, your first step should be to check if there is a known table with food on it. To do this, you need to determine whether there is food on a table. You can create a function called 'has_food_on_table(table:item)', which returns the result of the expression 'exists o: item : is_food(o) and on(o, table)'. This expression checks if there is an item classified as food that is on the table, according to your known information.
Next, you can use the expression 'exists table: item : is_table(table) and has_food_on_table(table)' to verify if there is a table with food on it in the known information. If such a table exists, there is no need to continue searching; you can immediately use 'walk_to(table)' to have the character approach the table with food.
However, if your known information does not confirm the presence of a table with food on it, you will need to inspect all unvisited items in the scene categorized as tables. To do this, you should call the 'observe' behavior to check each table. The first parameter of the 'observe' behavior should be the table you intend to inspect, and the second parameter should be the purpose of the inspection. Remember, the second parameter must be a string enclosed in double quotes ("").

Output:
def has_food_on_table(table:item):
    # Function to check if there is food on a specified table.
    symbol has_food=exists o: item : (is_food(o) and on(o, table))
    return has_food

behavior __goal__():
    body:
        if exists table: item : is_table(table) and has_food_on_table(table):
            # Check if there is a table with food based on the available information.
            bind table: item where:
                is_table(table) and has_food_on_table(table) # The condition has_food_on_table can only be used when you are certain that there is food on the table. In this case, you can be confident because you have already verified it with an if condition.
            # Select a table that has food on it.
            walk_to(table) 
            # Move the character closer to the table with food.

        else: 
           # If no table with food is found, initiate exploration to locate one.
            foreach table: item:
                if is_table(table) and not visited(table):
                    # Check all unvisited tables.
                    observe(table,"Check is there any food on the table")
                    # Observe whether each table has any food.
            
# Example-1-2:
Current sub-task goal: 2. Put the food in the appropriate storage locations.
The completed sub-tasks: 1. Find a table with food.
Additional information: 
1. There is no food on table 107. 
2. No food is find on the table 355, please see other tables.
3. food_peanut_butter_2008 and food_kiwi_2012 are on the table_226.
Long-horizon task: Clean up the food on the table.

Chain of thought: You have already find the table with food. Now, your current sub-task goal is to store the food on the table in the appropriate location. According to the additional information, there is no food on table_107 and table_355. However, table_226 has food_peanut_butter and food_kiwi.You can use the 'bind' keyword along with the condition 'is_table(table) and id[table] == 226' to obtain the table with the ID 226. You can also use the 'bind' keyword with the condition 'is_food_peanut_butter(food_peanut_butter)' to obtain the peanut butter. And use 'bind' keyword with the condition 'is_food_kiwi(food_kiwi)' to obtain the kiwi. Since the sub-task goal and additional information do not specify where exactly to store the food, you need to use common sense to make a decision based on the items present in the scene. Based on common sense, both food_peanut_butter and food_kiwi may require refrigeration, and since there is a fridge available in the scene, the goal is to store them in the fridge. Although it is not explicitly stated, it is common sense to ensure that the fridge door is closed after storing food inside. Therefore, you can use closes(fridge) to perform the action of closing the fridge door.

Output:
behavior store_in_fridge(food:item, fridge:item):
    body:
        put_inside(food, fridge)
        # Place the food item inside the fridge.

behavior close_the_fridge_door(fridge:item):
    body:
        closes(fridge)
        # Close the fridge door.

behavior __goal__():
    body:
        bind table: item where:
            is_table(table) and id[table]==226
        # Select table with ID 226.

        bind food_peanut_butter: item where:
            is_food_peanut_butter(food_peanut_butter)
        # Select peanut butter on the table.

        bind food_kiwi: item where:
            is_food_kiwi(food_kiwi)
        # Select kiwi on the table.
        
        bind fridge: item where:
            is_fridge(fridge)
        store_in_fridge(food_peanut_butter, fridge)
        store_in_fridge(food_kiwi, fridge)
        close_the_fridge_door(fridge)

# Example-1-3:
Current sub-task goal: 2. Put the food in the appropriate storage locations.
The completed sub-tasks: 1. Find a table with food.
Additional information: 
1. There is no food on table 107. 
2. No food is find on the table 355, please see other tables.
3. food_peanut_butter_2008 and food_kiwi_2012 are on the table_226.
4. The peanut butter is expired, so I want to throw it away. I want to cut the kiwi and then store it in the fridge.
Long-horizon task: Clean up the food on the table.

Chain of thought: According to Additional information 4, you need to discard the peanut butter. Observing that there is an "is_trashcan" in the Available Category, you can infer that there is a trashcan in the scene, and the expired peanut butter can be thrown into the trashcan. Additional information 4 also requires that the kiwi be cut, and then stored in the fridge. You need to use "cuts(food_kiwi)" to cut the kiwi. After that, you can "put_inside(food_kiwi, fridge)" to store the kiwi in the fridge. To ensure the completeness of the task, you also need to use "closes(fridge)" to make sure the fridge door is closed at the end by "closes(fridge)".

Output:
behavior throw_in_trash(food:item, trashcan:item): 
# Define the behavior to throw food into the trash can
    body:
        put_inside(food, trashcan)
        
behavior cut_food(food:item):
    body:
        cuts(food)

behavior store_in_fridge(food:item, fridge:item):
    body:
        put_inside(food, fridge)

behavior close_the_fridge_door(fridge:item):
    body:
        closes(fridge)

behavior __goal__():
    body:
        bind table: item where:
            is_table(table) and id[table]==226
        # Select table with ID 226.
        bind food_peanut_butter: item where:
            is_food_peanut_butter(food_peanut_butter)
        # Select peanut butter on the table.
        bind food_kiwi: item where:
            is_food_kiwi(food_kiwi)
        # Select kiwi on the table.
        bind trashcan: item where:
            is_trashcan(trashcan)
        # Select a trash can.
        bind fridge: item where:
            is_fridge(fridge)
        # Select a fridge.
        throw_in_trash(food_peanut_butter, trashcan)
        cut_food(food_kiwi)
        store_in_fridge(food_peanut_butter, fridge)
        close_the_fridge_door(fridge)
          
# Example-2-1:
Current sub-task goal: 1. Find the sink with plates and cups.
The completed sub-tasks: None, it is the first sub-task.
Additional information: None.
Long-horizon task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought: Your current sub-task goal is to find the sink with plates and cups, which is the first step toward completing the long-horizon task: "Wash the plates and cups in the sink using the dishwasher. Then put them on the table in the kitchen."
To achieve this, you first need to determine whether there are plates or cups in the sink. You can design a function called 'has_plate_or_cup_in_sink(sink:item)' that checks for this. The function should return the result of the expression 'exists o: item : (is_plate(o) or is_cup(o)) and inside(o, sink)', which verifies if there is an item that is either a plate or a cup and is located inside the sink in your known information.
Next, you can use 'exists sink: item : is_sink(sink) and has_plate_or_cup_in_sink(sink)' to check if there is a sink with plates or cups in it within the known information. If such a sink is found, there's no need to search further; you can immediately use 'walk_to(sink)' to have the character approach the sink containing the plates or cups.
However, if your known information does not confirm the presence of a sink with plates or cups, you will need to check all unvisited items categorized as sinks in the scene. For this, you should call the 'observe' behavior to inspect each sink. The first parameter of the 'observe' behavior should be the sink you intend to check, and the second parameter should be the purpose of the inspection. Remember, the second parameter must be a string enclosed in double quotes ("").

Output:
def has_plate_or_cup_in_sink(sink:item):
    # Function to check if there are plates or cups in a specified sink.
    symbol has_plate_or_cup=exists o: item : ((is_plate(o) or is_cup(o)) and inside(o, sink))
    return has_plate_or_cup

behavior __goal__():
    body:
        if exists sink: item : is_sink(sink) and has_plate_or_cup_in_sink(sink):
            # If we have already found the sink with plates or cups, we can directly approach it
            bind sink: item where:
                is_sink(sink) and has_plate_or_cup_in_sink(sink)
            walk_to(sink)

        else:
            # Check all sinks in the scene that have not been visited
            foreach sink: item:
                if is_sink(sink) and not visited(sink):
                    observe(sink,"Check is there any plate or cup in the sink")

# Example-2-2:
Current sub-task goal: 2. Wash the plates and cups using the dishwasher.
The completed sub-tasks: 1. Find the sink with plates and cups.
Additional information: 
1. sink_42 is in the bathroom, and no plates or cups are found in it.
2. sink_231 is in the kitchen, and there are plates and cups in it.
Long-horizon task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought:
According to additional information, sink_42 does not contain plates or cups, while sink_231 does contain plates or cups. Now you have found the sink that contains plates or cups. The current sub-task's goal is "Wash the plates and cups using the dishwasher." Although it doesn't explicitly state that the plates and cups in the sink need to be cleaned, considering the objective of the long-horizon task, the actual goal of the current sub-task should be to clean the plates and cups in the sink. To clean the plates and cups in the sink using the dishwasher, you first need to load them into the dishwasher. Since it is unclear how many plates and cups are in the sink, the foreach keyword is used with the condition if is_plate(o) or is_cup(o) and inside(o, sink) to place all items that are plates or cups from the sink into the dishwasher. After that, you can execute closes(dishwasher) and switch_on(dishwasher) sequentially to start the dishwasher.

Output:
behavior load_dishwasher(o:item, dishwasher:item):
    body:
        put_inside(o, dishwasher)
        # Place the item inside the dishwasher.

behavior start_dishwasher(dishwasher:item):
    body:
        closes(dishwasher) # Close the dishwasher door.
        switch_on(dishwasher) # Turn on the dishwasher.

behavior __goal__():
    body:
        bind sink: item where:
            is_sink(sink) and id[sink]==231
        # Select sink with ID 231.
        bind dishwasher: item where:
            is_dishwasher(dishwasher)
        # Select a dishwasher.
        foreach o: item:
        # Load all plates and cups from the sink into the dishwasher.
            if is_plate(o) or is_cup(o) and inside(o, sink):
                load_dishwasher(o, dishwasher)
        start_dishwasher(dishwasher) # Start the dishwasher.

# Example-2-3:
Current sub-task goal: 3. Put the plates and cups on the table in the kitchen.
The completed sub-tasks: 1. Find the sink with plates and cups. 2. Wash the plates and cups using the dishwasher.
Additional information: 
1. plate_1000, plate_1001, cup_1002, cup_1003 is cleaned by dishwasher_2000.
Long-horizon task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought:
According to "The completed sub-tasks" and "Additional information," the plates and cups that need to be placed on the table have already been cleaned in a dishwasher, and they are currently in a dishwasher with an ID of 2000. The current sub-task requires you to place the plates and cups on a table located in the kitchen. There may be more than one table in the scene, so you need to design a function 'in_kitchen(table: item)' that returns the value of the expression 'exists room: item : is_kitchen(room) and inside(table, room)', which checks whether the given table is inside a kitchen. Next, you need to design a 'put_on_table' behavior to place the plates or cups on the table. To determine which table to use, you should apply 'put_on_table' to all the plates or cups that were originally in the dishwasher, placing them on the table. Finally, to ensure the dishwasher is properly reset, you can design a 'close_the_dishwasher' behavior to turn off and close the dishwasher.

Output:
def in_kitchen(table:item):
    # Function to check if a table is in the kitchen.
    symbol in_kitchen=exists room: item : (is_kitchen(room) and inside(table, room))
    return in_kitchen

def has_plates_or_cups_inside(dishwasher:item):
    # Function to check if there are plates or cups inside the dishwasher.
    symbol has_plates_or_cups=exists o: item : ((is_plate(o) or is_cup(o)) and inside(o, dishwasher))
    return has_plates_or_cups

behavior put_on_table(o:item, table:item):
    body:
        put_on(o, table) # Place the item on the table.

behavior close_the_dishwasher(dishwasher:item):
    body:
        switch_off(dishwasher) # Turn off the dishwasher.
        closes(dishwasher) # Close the dishwasher door.

behavior __goal__():
    body:
        bind table: item where:
            is_table(table) and in_kitchen(table)
        # Select a table in the kitchen.
        bind dishwasher: item where:
            is_dishwasher(dishwasher) and id[dishwasher]==2000
        # Select the dishwasher with ID 2000.
        foreach o: item:
        # Place all plates and cups originally in the dishwasher on the table.
            if is_plate(o) or is_cup(o) and inside(o, dishwasher):
                put_on_table(o, table)
        close_the_dishwasher(dishwasher) # Reset the dishwasher.

# Guidance-1:
The following example demonstrates the difference between using foreach and bind.

Please note that bind requires the use of the "where" keyword, while foreach must not use the "where" keyword under any circumstances.  
eg:
foreach c: item:
    if is_clothes(c) and inside(c,basket):
        put_inside(c, washing_machine)

bind basket: item where:
    is_basket_for_clothes(basket)

You can see that all the foreach statements are used without "where", while all the bind statements need to include "where".

# Guidance-3:
In some cases, there may be multiple instances of the same object type within a scene. Simply using 'is_category()' to constrain the object type might be insufficient for selecting a specific instance. To retrieve the desired object more precisely, there are generally two methods. 
1. Using the ID: If you know the instance's unique ID, you can directly reference it, for example:

bind dishwasher: item where:
    is_dishwasher(dishwasher) and id[dishwasher] == 2000.

2. Adding positional relationships: You can specify spatial relationships between instances, for example: 

bind table: item where:
    is_table(table) and inside(table, kitchen).

In more complex scenarios, you can follow the approach in Example 2-3 by designing a function that adds constraints to the bind operation, allowing you to accurately retrieve the target instance.
Example:
def in_kitchen(table:item):
    symbol in_kitchen=exists room: item : (is_kitchen(room) and inside(table, room))
    return in_kitchen
    ......
bind table: item where:
    is_table(table) and in_kitchen(table)

You can also use attributes, states, and other information to further refine your constraints for the bind operation. However, it is crucial to ensure that an object satisfying all conditions exists. If you add more conditions to the bind statement but no object meets all of them, the operation will fail. Therefore, be mindful of how constraints interact to avoid retrieval errors.

# Guidance-3:
The observe(obj:item, question:string) is a powerful but resource-intensive behavior. It allows you to examine an object based on observation, during which you need to specify what information you wish to obtain from the object. Due to the high cost of using observe, the quality of your questions is crucial for improving execution efficiency. Generally speaking, information such as the type of object or its state can be obtained by referring to the methods provided in 'Available Category Determination' and 'Available States', so you usually don't need to invoke the observe behavior for these details. Some situations where observe behavior is necessary include when you want to check what items are inside or on the item you observe. For example, if you want to see what's inside the oven, you can use 'observe(oven, "What's inside the oven?")', or if you want to check what's on the table, you can use 'observe(table, "check items on the table")'. Also, feel free to ask more questions in the observe behavior to get more detailed information. For example, If you want to check what's inside the oven and whether it's on the kitchen counter, you can use 'observe(oven, "What's inside the oven? Is it on the kitchen counter?")'.

## Output Requirements:
You need to think step by step to give resonable output. However, you can only output content similar to the 'Output' in the 'Example'. Do not include any explanation or any other symbols.
"""
    return prompt