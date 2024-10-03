def not_found_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None):
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

def unknown_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None,behavior_from_library=None):
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
- sleeping(x: character) # The character is sleeping.
- inhand(x: item) # A item is grasped by a character. Only use it when an item needs to be continuously held in your hand.
- visited(x: item) # The character has observed the item
Important Note: The inhand(x) state is unique. If you intend to use inhand(x), you must implement it using the achieve_once keyword. At the same time, please note that you can take at most two items. Having too many items in hand will result in no solution. At the same time, please note that you can take at most two items. Having too many items in hand will result in no solution.

## Available Relationships:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- on(x: item, y: item) # item x is on top of item y
- on_char(x: character, y: item) # character is on item y
- inside(x: item, y: item) # item x is inside item y, and y should be a container
- inside_char(x: character, y: item) # character is inside item y
- close(x: item, y: item) # item x is close to item y
- close_char(x: character, y: item) # character is close to item y
- facing(x: item, y: item) # item x is facing item y
- facing_char(x: character, y: item) # character is facing item y
Important Usage Notes: In relationships with the '_char' suffix, the first parameter must always be a char. For example, 'on' and 'on_char', 'inside' and 'inside_char', 'close' and 'close_char', 'facing' and 'facing_char'.

## Available Properties:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
- surfaces(x: item) #  Indicates that the item has a surface where things can be placed, such as a kitchen countertop or table.
- grabbable(x: item) # Indicates that the item can be grabbed by hand.
- sittable(x: item) # Indicates that the item can be sat on.
- lieable(x: item) # Indicates that the item can be lied on.
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
- person(x: item) # Indicates that the item is a person.
- body_part(x: item) # Indicates that the item is a body part.
- cover_object(x: item)
- has_plug(x: item) # Indicates that the item has a plug.
- has_paper(x: item) # Indicates that the item contains paper.
- movable(x: item) # Indicates that the item can be moved.
- cream(x: item) # Indicates that the item is a cream.
- is_clothes(x: item) # Indicates that the item is clothing.
- is_food(x: item) # Indicates that the item is food.
Important Notes: "propertie" cannot be assigned a value nor can it be used after "achieve".; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions or assert statements.
Common Errors:
achieve can_open(door) # Incorrect. Properties cannot be used after achieve as they cannot have their values modified.
has_plug(lamp) = True # Incorrect. You cannot assign a value to a property, as they are immutable.

# Available Behaviors:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
The following behaviors can be directly invoked in the current sub-task goal representation, with parameters passed in like function arguments.
- observe(obj:item,question:string) # observe is a special behavior used to inspect an object. You can specify the purpose of your inspection with a string. By calling observe, you can learn about the state of an object as well as its relationship with surrounding objects. After observing an item, it will be marked as visited. Note that the second parameter of observe is a string and must be enclosed in double quotes("").
- wash(obj:item) # Wash an item by hand.
- scrub(obj:item) # Scrub an item.
- squeeze(obj:item) # Squeeze an item.
- rinse(obj:item) # Rinse an item.
- move(obj:item) # Move an item.
- pull(obj:item) # Pull an item.
- push(obj:item) # Push an item.
- greet(person:item) # Greet a person.
- look_at(obj:item) # Look at an item.
- drink(obj: item) # Drink an item.
- watch(obj:item) # Watch an item.
- type(obj:item) # Type on an item.
- touch(obj:item) # Touch an item.
- read(obj:item) # Read an item.
- water(obj:item) # Fill item with water.
- sit_somewhere(location:item) # Sit at a specific location.
- lie_somewhere(location:item) # Lie at a specific location.
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
"char" is a constant instance representing a character (yourself). The type "character" can only be used when defining an instance. Use "char" consistently when passing parameters, and use "character" when defining a variable and specifying its type.

Below are all the keywords you can use to convert information into a structured format. Please ensure that you do not use any keywords other than those listed here.

Keywords:
# bind
# Usage: Select an item that meets the specified conditions and assign it to a variable. To maintain consistency, try to use 'bind' primarily in the '__goal__' behavior and pass the retrieved instances as parameters to invoked behaviors. Avoid using 'bind' in other behaviors whenever possible.
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

# achieve
# Usage: Specifies the state or relationship that needs to be achieved. Only states and relationships can follow 'achieve', not types, properties, or other immutable content. Do not call functions or behaviors after 'achieve'; instead, call functions directly without keywords. Note that 'achieve' cannot be used with the state 'inhand'.
Example: achieve is_on(light)

# achieve_once
# Usage: Specifies a temporary state or relationship that needs to be achieved only once, without maintaining it until the end of the behavior.
Example: achieve_once inhand(apple) #Please note that 'inhand' must be used with 'achieve_once.'

# foreach
# Usage: Iterates over all objects of a certain type. Do not use 'where' in a 'foreach' statement.
Correct example:
foreach o: item:
    achieve closed(o)

Incorrect example:
foreach o: item where:
    achieve closed(o)

# behavior
# Usage: Defines a behavior rule. The keyword 'body' must appear in the behavior, and all parameters used in the 'goal' must be included in the behavior's parameters.

# goal
# Usage: Specifies the goal condition for a behavior. If you want to use the goal, please ensure that you include all the parameters used in the 'goal' in the behavior parameters.

# body
# Usage: Contains the sequence of intermediate states and relationships necessary to achieve the behavior’s goal.

# assert
# Usage: Asserts a condition that must be true for the behavior to succeed.
Example: assert is_on(light)

#assert_hold
# Usage: Maintains a long-term constraint until the end of the containing behavior.
Example: assert_hold closed(freezer)
ensures that the freezer remains closed until all behaviors are completed.
    
# eff
# Usage: Represents the effect of a behavior. In this section, perform a series of boolean assignments. Use '[]' instead of '()' here. This keyword is used only in transition models.
Example Transition Model:
When you have additional information like this: A vacuum cleaner is a great tool for cleaning floors. You can carry it around to clean the floor. Before using it, please make sure the vacuum cleaner is plugged in and turned on.
You should include this transition model in your output:
behavior clean_floow_with_vacuum(floor:item):
    goal: clean(floor)
    body:
        bind vacuum: item where:
            is_vacuum_cleaner(vacuum)
        achieve_once inhand(vacuum)
        achieve is_on(vacuum)
        achieve walk(floor)
    eff:
        clean[floor]=True

# if-else
# Usage: Conditional statement for branching logic.
if condition:
    achieve close(a)
else:
    achieve clean(b)

# exists
# Usage: Checks if there is at least one object that meets the condition and returns a boolean value.
Template: exists obj_name: objtype : condition()
Example: exists item1: item : holds_lh(char, item1)

# symbol
# Usage: Defines a symbol and binds it to the output of an expression. You can only use the symbol in the following manner:
symbol l=exists item1: item : holds_lh(char, item1)

# def
# Usage: Defines a function that can be used to check a condition. 

## Example:
Please refer to the method used in the example below to modify the goal representation I provided in this round, supplementing the missing definitions and declarations. Each example below will provide both wrong and correct versions, so you can learn how I make the modifications.

- Wrong Version(light in make_dinner is not defined):
behavior make_dinner():
    body:
        achieve is_on(light)

-> corrected version:
behavior make_dinner(light:item):
    body:
        achieve is_on(light)
    
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
behavior drop(inhand_obj:item,location:item):
  goal: not inhand(inhand_obj)
  body:
    put(inhand_obj, location)

In this example, the original version of the behavior definition contains an undefined variable location in the body of the behavior "drop". To correct this, I added the bind statement to define the variable location.   

- Wrong Version(use "self" instead of "char"):
behavior view_neighborhood_from_child_room_window():
    body:
        bind window: item where:
            is_window(window)
        achieve inside_char(self, child_room)

-> corrected version:
behavior view_neighborhood_from_child_room_window():
    body:
        bind window: item where:
            is_window(window)
        achieve inside_char(char, child_room)

In this example, the original version of the behavior definition contains an undefined variable self in the body of the behavior "view_neighborhood_from_child_room_window". Use "char" directly to represent itself.

Please note that, you can not provide any parameters to __goal__().
At the same time, please note that when you modify the parameters of a function or behavior, don't forget to also modify the function or behavior call statements to add any missing parameters.

## Output Format:
Output the goal representation with the supplemented definitions and declarations. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt

def other_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None,behavior_from_library=None):
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
- Double-check for any issues that might prevent the program from running, particularly in relation to the definitions and usage of transition models. Note that the __goal__ behavior should not be a transition model.

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
- sleeping(x: character) # The character is sleeping.
- inhand(x: item) # A item is grasped by a character. Only use it when an item needs to be continuously held in your hand.
- visited(x: item) # The character has observed the item
Important Note: The inhand(x) state is unique. If you intend to use inhand(x), you must implement it using the achieve_once keyword. At the same time, please note that you can take at most two items. Having too many items in hand will result in no solution. At the same time, please note that you can take at most two items. Having too many items in hand will result in no solution.

## Available Relationships:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- on(x: item, y: item) # item x is on top of item y
- on_char(x: character, y: item) # character is on item y
- inside(x: item, y: item) # item x is inside item y, and y should be a container
- inside_char(x: character, y: item) # character is inside item y
- close(x: item, y: item) # item x is close to item y
- close_char(x: character, y: item) # character is close to item y
- facing(x: item, y: item) # item x is facing item y
- facing_char(x: character, y: item) # character is facing item y
Important Usage Notes: In relationships with the '_char' suffix, the first parameter must always be a char. For example, 'on' and 'on_char', 'inside' and 'inside_char', 'close' and 'close_char', 'facing' and 'facing_char'.

## Available Properties:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
- surfaces(x: item) #  Indicates that the item has a surface where things can be placed, such as a kitchen countertop or table.
- grabbable(x: item) # Indicates that the item can be grabbed by hand.
- sittable(x: item) # Indicates that the item can be sat on.
- lieable(x: item) # Indicates that the item can be lied on.
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
- person(x: item) # Indicates that the item is a person.
- body_part(x: item) # Indicates that the item is a body part.
- cover_object(x: item)
- has_plug(x: item) # Indicates that the item has a plug.
- has_paper(x: item) # Indicates that the item contains paper.
- movable(x: item) # Indicates that the item can be moved.
- cream(x: item) # Indicates that the item is a cream.
- is_clothes(x: item) # Indicates that the item is clothing.
- is_food(x: item) # Indicates that the item is food.
Important Notes: "propertie" cannot be assigned a value nor can it be used after "achieve".; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions or assert statements.
Common Errors:
achieve can_open(door) # Incorrect. Properties cannot be used after achieve as they cannot have their values modified.
has_plug(lamp) = True # Incorrect. You cannot assign a value to a property, as they are immutable.

# Available Behaviors:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation.
The following behaviors can be directly invoked in the current sub-task goal representation, with parameters passed in like function arguments.
- observe(obj:item,question:string) # observe is a special behavior used to inspect an object. You can specify the purpose of your inspection with a string. By calling observe, you can learn about the state of an object as well as its relationship with surrounding objects. After observing an item, it will be marked as visited. Note that the second parameter of observe is a string and must be enclosed in double quotes("").
- wash(obj:item) # Wash an item by hand.
- scrub(obj:item) # Scrub an item.
- squeeze(obj:item) # Squeeze an item.
- rinse(obj:item) # Rinse an item.
- move(obj:item) # Move an item.
- pull(obj:item) # Pull an item.
- push(obj:item) # Push an item.
- greet(person:item) # Greet a person.
- look_at(obj:item) # Look at an item.
- drink(obj: item) # Drink an item.
- watch(obj:item) # Watch an item.
- type(obj:item) # Type on an item.
- touch(obj:item) # Touch an item.
- read(obj:item) # Read an item.
- water(obj:item) # Fill item with water.
- sit_somewhere(location:item) # Sit at a specific location.
- lie_somewhere(location:item) # Lie at a specific location.
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
"char" is a constant instance representing a character (yourself). The type "character" can only be used when defining an instance. Use "char" consistently when passing parameters, and use "character" when defining a variable and specifying its type.

Below are all the keywords you can use to convert information into a structured format. Please ensure that you do not use any keywords other than those listed here.

Keywords:
# bind
# Usage: Select an item that meets the specified conditions and assign it to a variable. To maintain consistency, try to use 'bind' primarily in the '__goal__' behavior and pass the retrieved instances as parameters to invoked behaviors. Avoid using 'bind' in other behaviors whenever possible.
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

# achieve
# Usage: Specifies the state or relationship that needs to be achieved. Only states and relationships can follow 'achieve', not types, properties, or other immutable content. Do not call functions or behaviors after 'achieve'; instead, call functions directly without keywords. Note that 'achieve' cannot be used with the state 'inhand'.
Example: achieve is_on(light)

# achieve_once
# Usage: Specifies a temporary state or relationship that needs to be achieved only once, without maintaining it until the end of the behavior.
Example: achieve_once inhand(apple) #Please note that 'inhand' must be used with 'achieve_once.'

# foreach
# Usage: Iterates over all objects of a certain type. Do not use 'where' in a 'foreach' statement.
Correct example:
foreach o: item:
    achieve closed(o)

Incorrect example:
foreach o: item where:
    achieve closed(o)

# behavior
# Usage: Defines a behavior rule. The keyword 'body' must appear in the behavior, and all parameters used in the 'goal' must be included in the behavior's parameters.

# goal
# Usage: Specifies the goal condition for a behavior. If you want to use the goal, please ensure that you include all the parameters used in the 'goal' in the behavior parameters.

# body
# Usage: Contains the sequence of intermediate states and relationships necessary to achieve the behavior’s goal.

# assert
# Usage: Asserts a condition that must be true for the behavior to succeed.
Example: assert is_on(light)

#assert_hold
# Usage: Maintains a long-term constraint until the end of the containing behavior.
Example: assert_hold closed(freezer)
ensures that the freezer remains closed until all behaviors are completed.
    
# eff
# Usage: Represents the effect of a behavior. In this section, perform a series of boolean assignments. Use '[]' instead of '()' here. This keyword is used only in transition models.
Example Transition Model:
When you have additional information like this: A vacuum cleaner is a great tool for cleaning floors. You can carry it around to clean the floor. Before using it, please make sure the vacuum cleaner is plugged in and turned on.
You should include this transition model in your output:
behavior clean_floow_with_vacuum(floor:item):
    goal: clean(floor)
    body:
        bind vacuum: item where:
            is_vacuum_cleaner(vacuum)
        achieve_once inhand(vacuum)
        achieve is_on(vacuum)
        achieve walk(floor)
    eff:
        clean[floor]=True

# if-else
# Usage: Conditional statement for branching logic.
if condition:
    achieve close(a)
else:
    achieve clean(b)

# exists
# Usage: Checks if there is at least one object that meets the condition and returns a boolean value.
Template: exists obj_name: objtype : condition()
Example: exists item1: item : holds_lh(char, item1)

# symbol
# Usage: Defines a symbol and binds it to the output of an expression. You can only use the symbol in the following manner:
symbol l=exists item1: item : holds_lh(char, item1)

# def
# Usage: Defines a function that can be used to check a condition. 

## Background Knowledge:
In general, you only know part of the information in a given scenario. For example, you might know that a certain piece of clothing is in a particular basket, but you might not know what is in a certain basket. Therefore, many times, you need to first perform a goal conversion based on what you already know. When you lack some information, you can observe and obtain the information you want by using obs(target_item, information).
For example,if you want to know if there any clothes in the basket_34, you can use:
bind basket: item where:
    is_basket(basket) and id[basket]==34
observe(basket,"Check is there any clothes in the basket")

If you want to know Is there any trash in the trash can in the dining room, you can use:
def in_the_diining_room(trash_can:item):
    symbol in_dining_room=exists room: item : is_dining_room(room) and inside(trash_can, room)
    return in_dining_room

bind trash_can: item where:
    is_trash_can(trash_can) and in_the_diining_room(trash_can)
observe(trash_can,"Check is there any trash in the trash can")

## Examples:
## Example-1-1:
Current sub-task goal: 1. Find a table with food.
The completed sub-tasks: None, it is the first sub-task.
Additional information: None.
Long-horizon task: Clean up the food on the table.
Chain of thought: Your current sub-task goal is to find a table with food on it, which is the first step towards completing the long-horizon task: "Clean up the food on the table."
According to the background knowledge, your first step should be to check if there is a known table with food on it. To do this, you need to determine whether there is food on a table. You can create a function called 'has_food_on_table(table:item)', which returns the result of the expression 'exists o: item : is_food(o) and on(o, table)'. This expression checks if there is an item classified as food that is on the table, according to your known information.
Next, you can use the expression 'exists table: item : is_table(table) and has_food_on_table(table)' to verify if there is a table with food on it in the known information. If such a table exists, there is no need to continue searching; you can immediately use 'achieve close_char(char, table)' to have the character approach the table with food.
However, if your known information does not confirm the presence of a table with food on it, you will need to inspect all unvisited items in the scene categorized as tables. To do this, you should call the 'observe' behavior to check each table. The first parameter of the 'observe' behavior should be the table you intend to inspect, and the second parameter should be the purpose of the inspection. Remember, the second parameter must be a string enclosed in double quotes ("").

Output:
def has_food_on_table(table:item):
    symbol has_food=exists o: item : is_food(o) and on(o, table)
    return has_food

behavior __goal__():
    body:
        if exists table: item : is_table(table) and has_food_on_table(table):
            bind table: item where:
                is_table(table) and has_food_on_table(table)
            achieve close_char(char, table)

        else:
            foreach table: item:
                if is_table(table) and not visited(table):
                    observe(table,"Check is there any food on the table")
            
Output Analysis: In this output, function 'has_food_on_table' is used to check whether there is food on a table. It does so by defining a 'has_food' variable using the symbol keyword. This variable is an expression that evaluates to true if food exists and is located on the specified table. The function then returns the value of the 'has_food' variable.
The '__goal__()' behavior is a structure that must be included in the output, similar to the main function in Python. In '__goal__', the logic for finding the table is designed. If there is a table in the scene that satisfies 'has_food_on_table', then the table is bound using the bind statement. And the "achieve close_char(char,table)" ensures the agent get close to that table with food. If there isn't a table that satisfies 'has_food_on_table', maybe there are still some tables in the scene that haven't been visited yet, then observe these tables one by one. When observing a table, your purpose is to check if there is any food on it. Please note that the second parameter of 'observe' is a string and must be enclosed in double quotes.

# Example-1-2:
Current sub-task goal: 2. Put the food in the appropriate storage locations.
The completed sub-tasks: 1. Find a table with food.
Additional information: 
1. There is no food on table 107. 
2. No food is find on the table 355, please see other tables.
3. food_peanut_butter_2008 and food_kiwi_2012 are on the table_226.
Long-horizon task: Clean up the food on the table.

Chain of thought: You have already find the table with food. Now, your current sub-task goal is to store the food on the table in the appropriate location. According to the additional information, there is no food on table_107 and table_355. However, table_226 has food_peanut_butter and food_kiwi.You can use the 'bind' keyword along with the condition 'is_table(table) and id[table] == 226' to obtain the table with the ID 226. You can also use the 'bind' keyword with the condition 'is_food_peanut_butter(food_peanut_butter) and on(food_peanut_butter, table)' to obtain the peanut butter that is on the table 226. And use 'bind' keyword with the condition 'is_food_kiwi(food_kiwi) and on(food_kiwi, table)' to obtain the kiwi on the table 226. Since the sub-task goal and additional information do not specify where exactly to store the food, you need to use common sense to make a decision based on the items present in the scene. Based on common sense, both food_peanut_butter and food_kiwi may require refrigeration, and since there is a freezer available in the scene, the goal is to store them in the freezer. Although it is not explicitly stated, it is common sense to ensure that the refrigerator door is closed after storing food inside. Therefore, you can use achieve closed(freezer) to perform the action of closing the refrigerator door.

Output:
behavior store_in_freezer(food:item, freezer:item):
    body:
        achieve inside(food, freezer)

behavior close_the_freezer_door(freezer:item):
    body:
        achieve closed(freezer)

behavior __goal__():
    body:
        bind table: item where:
            is_table(table) and id[table]==226
        bind food_peanut_butter: item where:
            is_food_peanut_butter(food_peanut_butter) and on(food_peanut_butter, table)
        bind food_kiwi: item where:
            is_food_kiwi(food_kiwi) and on(food_kiwi, table)
        bind freezer: item where:
            is_freezer(freezer)
        store_in_freezer(food_peanut_butter, freezer)
        store_in_freezer(food_kiwi, freezer)
        close_the_freezer_door(freezer)

Output Analysis: 
The function 'store_in_freezer' is implemented to store food in the freezer. In the '__goal__', the bind table operation adds two constraints: 'is_table(table)' and 'id[table]==226', ensuring that the table instance selected is specifically table_226. When subsequently using 'bind' to select 'food_peanut_butter' and 'food_kiwi', special care must be taken to ensure that these foods are indeed on the table, which aligns with the current objective. Finally, 'bind' is used to select the freezer from the scene for storing the food.

# Example-1-3:
Current sub-task goal: 2. Put the food in the appropriate storage locations.
The completed sub-tasks: 1. Find a table with food.
Additional information: 
1. There is no food on table 107. 
2. No food is find on the table 355, please see other tables.
3. food_peanut_butter_2008 and food_kiwi_2012 are on the table_226.
4. The peanut butter is expired, so I want to throw it away. I want to cut the kiwi and then store it in the freezer.
Long-horizon task: Clean up the food on the table.

Chain of thought: According to Additional information 4, you need to discard the peanut butter. Observing that there is an "is_trashcan" in the Available Category, you can infer that there is a trashcan in the scene, and the expired peanut butter can be thrown into the trashcan. Additional information 4 also requires that the kiwi be washed, cut, and then stored in the refrigerator. Based on common sense, the kiwi can be washed in the sink, and then you need to use "achieve cut(food_kiwi)" to cut the kiwi. After that, you can "achieve inside(food_kiwi, freezer)" to store the kiwi in the freezer. To ensure the completeness of the task, you also need to use "achieve closed(freezer)" to make sure the refrigerator door is closed at the end by "achieve closed(freezer)".

Output:
behavior throw_in_trash(food:item, trashcan:item):
    body:
        achieve inside(food, trashcan)

behavior clean_food(food:item, sink:item):
    body:
        achieve_once inside(food, sink)
        if exists faucet:item: is_faucet(faucet) and close(faucet,sink):
            bind faucet: item where:
                is_faucet(faucet) and close(faucet,sink)
            achieve_once is_on(faucet)
        wash(food)
        if exists faucet:item: is_faucet(faucet) and close(faucet,sink):
            bind faucet: item where:
                is_faucet(faucet) and close(faucet,sink)
            achieve_once is_on(faucet)
        
behavior cut_food(food:item):
    body:
        achieve cut(food)

behavior store_in_freezer(food:item, freezer:item):
    body:
        achieve inside(food, freezer)

behavior close_the_freezer_door(freezer:item):
    body:
        achieve closed(freezer)

behavior __goal__():
    body:
        bind table: item where:
            is_table(table) and id[table]==226
        bind food_peanut_butter: item where:
            is_food_peanut_butter(food_peanut_butter) and on(food_peanut_butter, table)
        bind food_kiwi: item where:
            is_food_kiwi(food_kiwi) and on(food_kiwi, table)
        bind trashcan: item where:
            is_trashcan(trashcan)
        bind sink: item where:
            is_sink(sink)
        bind freezer: item where:
            is_freezer(freezer)
        throw_in_trash(food_peanut_butter, trashcan)
        clean_food(food_kiwi, sink)
        cut_food(food_kiwi)
        store_in_freezer(food_peanut_butter, freezer)
        close_the_freezer_door(freezer)

Output Analysis: 
The 'throw_in_trash' is used to throw food into the trash can. In 'clean_food', first, use 'achieve_once inside(food, sink)' to ensure the food is placed in the sink. Then, if there is a faucet near the sink, turn it on. Note that 'achieve_once is_on' and 'achieve_once is_off' should be used here. Since the duration of achieve lasts throughout the entire behavior, using 'achieve is_on' and 'achieve is_off' would require the faucet to remain both on and off during the 'clean_food' behavior, which would cause the program to be unsolvable. All mutually exclusive states within the same behavior need to be implemented using 'achieve_once'. The 'clean_food' behavior also includes an intermediate wash behavior to perform the action of washing the food. The 'cut_food', 'store_in_freezer', and 'close_the_freezer_door' behaviors are used to cut the food, store the food in the freezer, and ensure that the freezer door is closed at the end of the task, respectively. In the '__goal__' behavior, most of the bind operations are implemented, and the previously defined behaviors are called in sequence.
          
# Example-2-1:
Current sub-task goal: 1. Find the sink with plates and cups.
The completed sub-tasks: None, it is the first sub-task.
Additional information: None.
Long-horizon task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought: Your current sub-task goal is to find the sink with plates and cups, which is the first step toward completing the long-horizon task: "Wash the plates and cups in the sink using the dishwasher. Then put them on the table in the kitchen."
To achieve this, you first need to determine whether there are plates or cups in the sink. You can design a function called 'has_plate_or_cup_in_sink(sink:item)' that checks for this. The function should return the result of the expression 'exists o: item : (is_plate(o) or is_cup(o)) and inside(o, sink)', which verifies if there is an item that is either a plate or a cup and is located inside the sink in your known information.
Next, you can use 'exists sink: item : is_sink(sink) and has_plate_or_cup_in_sink(sink)' to check if there is a sink with plates or cups in it within the known information. If such a sink is found, there's no need to search further; you can immediately use 'achieve close_char(char, sink)' to have the character approach the sink containing the plates or cups.
However, if your known information does not confirm the presence of a sink with plates or cups, you will need to check all unvisited items categorized as sinks in the scene. For this, you should call the 'observe' behavior to inspect each sink. The first parameter of the 'observe' behavior should be the sink you intend to check, and the second parameter should be the purpose of the inspection. Remember, the second parameter must be a string enclosed in double quotes ("").

Output:
def has_plate_or_cup_in_sink(sink:item):
    symbol has_plate_or_cup=exists o: item : (is_plate(o) or is_cup(o)) and inside(o, sink)
    return has_plate_or_cup

behavior __goal__():
    body:
        if exists sink: item : is_sink(sink) and has_plate_or_cup_in_sink(sink):
            bind sink: item where:
                is_sink(sink) and has_plate_or_cup_in_sink(sink)
            achieve close_char(char, sink)

        else:
            foreach sink: item:
                if is_sink(sink) and not visited(sink):
                    observe(sink,"Check is there any plate or cup in the sink")
    
Output Analysis: 
A function is defined using the 'def' keyword to check whether there are plates or bowls in the sink. The return value of the function is the value of the expression “exists o: item : (is_plate(o) or is_cup(o)) and inside(o, sink)”. This expression means checking if there is an object of the type plate or cup that is inside the sink. If the return value is true, it indicates that there is a plate or a cup in the sink.
In "__goal__", the statement 'if exists sink: item : is_sink(sink) and has_plate_or_cup_in_sink(sink)' is used to check if there is a sink that contains a plate or a cup. If such a sink exists, the 'bind' keyword is used to select this sink with the condition 'is_sink(sink) and has_plate_or_cup_in_sink(sink)'. Then, 'achieve close_char(char, sink)' is used to make the character approach this sink.
If there is no sink containing a plate or cup, it is necessary to check the sinks in the scene that have not yet been visited. The output calls 'observe(sink, "Check if there is any plate or cup in the sink")' to observe whether these unvisited sinks contain a plate or cup.

# Example-2-2:
Current sub-task goal: 2. Wash the plates and cups using the dishwasher.
The completed sub-tasks: 1. Find the sink with plates and cups.
Additional information: 
1. sink_42 is in the bathroom, and no plates or cups are found in it.
2. sink_231 is in the kitchen, and there are plates and cups in it.
Long-horizon task: Wash the plates and cups in the sink using the dishwasher. Then put them on the table in kitchen.

Chain of thought:
According to additional information, sink_42 does not contain plates or cups, while sink_231 does contain plates or cups. Now you have found the sink that contains plates or cups. The current sub-task's goal is "Wash the plates and cups using the dishwasher." Although it doesn't explicitly state that the plates and cups in the sink need to be cleaned, considering the objective of the long-horizon task, the actual goal of the current sub-task should be to clean the plates and cups in the sink. To clean the plates and cups in the sink using the dishwasher, you first need to load them into the dishwasher. Since it is unclear how many plates and cups are in the sink, the foreach keyword is used with the condition if is_plate(o) or is_cup(o) and inside(o, sink) to place all items that are plates or cups from the sink into the dishwasher. After that, you can execute achieve closed(dishwasher) and achieve is_on(dishwasher) sequentially to start the dishwasher.

Output:
behavior load_dishwasher(o:item, dishwasher:item):
    body:
        achieve inside(o, dishwasher)

behavior start_dishwasher(dishwasher:item):
    body:
        achieve closed(dishwasher)
        achieve is_on(dishwasher)

behavior __goal__():
    body:
        bind sink: item where:
            is_sink(sink) and id[sink]==231
        bind dishwasher: item where:
            is_dishwasher(dishwasher)
        foreach o: item:
            if is_plate(o) or is_cup(o) and inside(o, sink):
                load_dishwasher(o, dishwasher)
        start_dishwasher(dishwasher)
        
Output Analysis: 
The 'load_dishwasher' behavior is implemented to place the items to be cleaned into the dishwasher. The 'start_dishwasher' behavior is implemented to start the dishwasher. In the '__goal__' behavior, it is important to note that according to additional information, sink_231 contains plates and cups, so when using the 'bind' operation to select the sink, you need to specify 'id[sink] == 231'. Then, use the 'bind' keyword to select a dishwasher. Next, use a 'foreach' loop to place all the plates and cups in the sink into the dishwasher. Finally, call 'start_dishwasher' to start the dishwasher and complete the cleaning process.

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
    symbol in_kitchen=exists room: item : is_kitchen(room) and inside(table, room)
    return in_kitchen

def has_plates_or_cups_inside(dishwasher:item):
    symbol has_plates_or_cups=exists o: item : (is_plate(o) or is_cup(o)) and inside(o, dishwasher)
    return has_plates_or_cups

behavior put_on_table(o:item, table:item):
    body:
        achieve on(o, table)

behavior close_the_dishwasher(dishwasher:item):
    body:
        achieve is_off(dishwasher)
        achieve closed(dishwasher)

behavior __goal__():
    body:
        bind table: item where:
            is_table(table) and in_kitchen(table)
        bind dishwasher: item where:
            is_dishwasher(dishwasher) and id[dishwasher]==2000
        foreach o: item:
            if is_plate(o) or is_cup(o) and inside(o, dishwasher):
                put_on_table(o, table)
        close_the_dishwasher(dishwasher)

Output Analysis: 
In the output, two functions are defined using the def keyword: 'in_kitchen', which determines whether a table is in the kitchen, and 'has_plates_or_cups_inside', which checks if a dishwasher contains plates or cups. Then, two additional behaviors are defined: 'put_on_table', used to place items on the table, and 'close_the_dishwasher', used to reset the dishwasher, ensuring that after the cleaning task is complete, the dishwasher is turned off and closed. In '__goal__', the 'bind' keyword is used with the condition 'is_table(table) and in_kitchen(table)' to select a table in the kitchen. Then, another 'bind' keyword is used with the condition 'is_dishwasher(dishwasher) and id[dishwasher]==2000' to select the dishwasher with ID 2000. After that, a foreach loop is used to call the 'put_on_table' behavior, placing all the plates and cups originally in the dishwasher onto the table. Finally, the 'close_the_dishwasher' behavior is used to reset the dishwasher.

#Guidance-1:
A common mistake is ignoring the effective duration of "achieve." The effective duration of "achieve" persists until the current action is completed. If you specify two mutually exclusive states in a behavior using "achieve," it will result in a program error.

Here is some typical errors:
- error example-1:
behavior put_apple_on_table(apple:item,table:item):
    body:
        achieve inhand(apple)
        achieve on(apple,table)

Error Analysis: In this example, if you use achieve inhand(apple), then the apple must be keep inhand until the end of this behavior. Then you use achieve on(apple,table), which means you put the apple on the table. Now the apple should be both remain in hand and be placed on the table, which is impossible to achieve. The solution to this problem is to remove the unnecessary step of achieving inhand(apple), as the program will automatically determine how to achieve on(apple,table). In fact, unless you need to hold an item to complete a specific task (such as cutting vegetables with a knife or wiping a window with a cloth), please avoid using the "inhand" state in other situations.

A correct output for example-1 is:
behavior put_apple_on_table(apple:item,table:item):
    body:
        achieve on(apple,table)

- error example-2:
behavior clean_a_vegetable_in_sink(vegetable:item,sink:item):
    body:
        achieve inside(vegetable,sink)
        if exists faucet:item: is_faucet(faucet) and close(faucet,sink):
            achieve is_on(faucet)
            wash(vegetable)
            achieve is_off(faucet)
        else:
            wash(vegetable)

Error Analysis: The problem with this example is that it uses both achieve is_on(faucet) and is_off(faucet) sequentially. These states are mutually exclusive, as the faucet should not be both on and off at the same time. To resolve this issue, you can use achieve_once to prevent achieve from persisting until the current behavior ends.

A correct output for example-2 is:
behavior clean_a_vegetable_in_sink(vegetable:item,sink:item):
    body:
        achieve inside(vegetable,sink)
        if exists faucet:item: is_faucet(faucet) and close(faucet,sink):
            achieve_once is_on(faucet)
            wash(vegetable)
            achieve_once is_off(faucet)
        else:
            wash(vegetable)

# Guidance-2:
The following example demonstrates the difference between using foreach and bind.

Please note that bind requires the use of the "where keyword", while foreach must not use the "where" keyword under any circumstances.  
eg:
foreach c: item:
    if is_clothes(c) and inside(c,basket):
        achieve inside(c, washing_machine)

foreach obj2:item:
    if inside(obj,obj2):
    if not is_room(obj2):
        assert can_open(obj2) or recipient(obj2) or eatable(obj2)
        if can_open(obj2):
        achieve open(obj2)

bind basket: item where:
    is_basket_for_clothes(basket)

bind washing_machine: item where:
    is_washing_machine(washing_machine)

You can see that all the foreach statements are used without "where", while all the bind statements need to include "where".

# Guidance-3:
Since there are usually more than one instance of the same type of object in a scene, simply using 'is_category()' to constrain the type of the object is often insufficient when selecting a specific instance. To more accurately retrieve the desired object, there are generally two methods. One is to directly use the id if you know the target instance's number, for example:"is_dishwasher(dishwasher) and id[dishwasher]==2000". The other is to add a positional relationship with other objects, such as selecting the faucet next to the sink. In more complex situations, you can follow the approach in Example-2-3 and design a function specifically for adding constraints to the bind operation, allowing you to accurately obtain the desired instance.
Example:
def in_kitchen(table:item):
    symbol in_kitchen=exists room: item : is_kitchen(room) and inside(table, room)
    return in_kitchen
    ......
bind table: item where:
    is_table(table) and in_kitchen(table)
Of course, you can also use attributes, states, and other information to more flexibly constrain the instances retrieved by the bind operation.

# Guidance-4:
The observe(obj:item, question:string) is a powerful but resource-intensive behavior. It allows you to examine an object based on observation, during which you need to specify what information you wish to obtain from the object. Due to the high cost of using observe, the quality of your questions is crucial for improving execution efficiency. Generally speaking, information such as the type of object or its state can be obtained by referring to the methods provided in 'Available Category Determination' and 'Available States', so you usually don't need to invoke the observe behavior for these details. Some situations where observe behavior is necessary include when you want to check what items are placed in a certain location. For example, if you want to see what's inside the oven, you can use 'observe(oven, "What's inside the oven?")', or if you want to check what's on the table, you can use 'observe(table, "check items on the table")'.

## Output Requirements:
You need to think step by step to give resonable output. However,
You can only output content similar to the 'Output' in the 'Example'. Do not include any explanation or any other symbols.

"""
    return prompt