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
Undefined category names are used in the goal representation.
For this situation, prioritize using synonyms to replace the undefined category names. If that's not possible, use categories with similar functions. However, under all circumstances, ensure that the corrected item categories appear in the available categories. I will demonstrate how to make replacements in the example section.

## The goal representations are:
""" + goal_representation + """

## error:
The goal representations include such undefined categories: """+error_info+"""
Please refer to the available representations below to make modifications here.

## available category determination:
"""+categories+"""
For any instance x:item, you can use is_y(x) to determine if x belongs to category y. You cannot perform any operations on a category; you can only determine the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use:
bind b: item where:
    is_box(b)

## available properties (The text following the hash symbol is a comment; please do not include it in the goal representation):
- surfaces(x: item) # To indicate an item has a surface where things can be placed, such as a kitchen countertop or a table.
- grabbable(x: item) # To indicate an item can be grabbed in hand.
- sittable(x: item) # To indicate an item can be sat on.
- lieable(x: item) # To indicate an item can be lied on.
- hangable(x: item) # To indicate an item can be hung on.
- drinkable(x: item) # To indicate an item can be drunk.
- eatable(x: item) # To indicate an item can be eaten.
- recipient(x: item) # To indicate an item can be used to receive something.
- cuttable(x: item) # To indicate an item can be cut with a knife.
- pourable(x: item) # To indicate an item can be poured into another container or on other items.
- can_open(x: item) # To indicate an item can be opened.
- has_switch(x: item) # To indicate an item has a switch to turn on or off.
- readable(x: item) # To indicate an item can be read.
- lookable(x: item) # To indicate an item can be looked at.
- containers(x: item) # To indicate an item is a container.
- clothes(x: item) # To indicate an item is a piece of clothing.
- person(x: item) 
- body_part(x: item)
- cover_object(x: item)
- has_plug(x: item) # To indicate an item has a plug.
- has_paper(x: item) # To indicate an item has paper.
- movable(x: item) # To indicate an item can be moved.
- cream(x: item) # To indicate an item is a cream.
properties cannot be assigned a value; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions or assert statements.

## Example:
- is_food() -> is_food_food(), Although the first type of translation is intuitive, when is_food is not in the available category, but is_food_food is, such a replacement should be made.
- is_soapy_water() -> is_cleaning_solution(), soapy water is not an available category, but cleaning solution is. They are functionally similar, so such a replacement should be made.

## Output Format:
Only replace the incorrect category names without modifying any other parts, including content and indentation. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt

def unknown_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None):
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

## The available states are:
- is_on(x: item) #is working
- is_off(x: item) #is not working
- plugged(x: item)
- unplugged(x: item)
- open(x: item)
- closed(x: item)
- dirty(x: item)
- clean(x: item)
- cut(x: item)
- sitting(x: character)
- lying(x: character)
- sleeping(x: character)
- inhand(x: item) # A item is grasped by a character

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
Here are a few easily confusing usages to note:
In relationships with the _char suffix, the first parameter must always be a char. For example, on and on_char, inside and inside_char, close and close_char, facing and facing_char.

## available properties (The text following the hash symbol is a comment; please do not include it in the goal representation):
- surfaces(x: item) # To indicate an item has a surface where things can be placed, such as a kitchen countertop or a table.
- grabbable(x: item) # To indicate an item can be grabbed in hand.
- sittable(x: item) # To indicate an item can be sat on.
- lieable(x: item) # To indicate an item can be lied on.
- hangable(x: item) # To indicate an item can be hung on.
- drinkable(x: item) # To indicate an item can be drunk.
- eatable(x: item) # To indicate an item can be eaten.
- recipient(x: item) # To indicate an item can be used to receive something.
- cuttable(x: item) # To indicate an item can be cut with a knife.
- pourable(x: item) # To indicate an item can be poured into another container or on other items.
- can_open(x: item) # To indicate an item can be opened.
- has_switch(x: item) # To indicate an item has a switch to turn on or off.
- readable(x: item) # To indicate an item can be read.
- lookable(x: item) # To indicate an item can be looked at.
- containers(x: item) # To indicate an item is a container.
- clothes(x: item) # To indicate an item is a piece of clothing.
- person(x: item) 
- body_part(x: item)
- cover_object(x: item)
- has_plug(x: item) # To indicate an item has a plug.
- has_paper(x: item) # To indicate an item has paper.
- movable(x: item) # To indicate an item can be moved.
- cream(x: item) # To indicate an item is a cream.
properties cannot be assigned a value; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions or assert statements.

## available category determination:
"""+categories+"""
For any instance x:item, you can use is_y(x) to determine if x belongs to category y. You cannot perform any operations on a category; you can only determine the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use:
bind b: item where:
    is_box(b)

## Syntax rules and keywords:
"char" is a constant instance that represents a character(youself). And character is a basic type, which can only be used when defining a instance. When passing parameters, use "char" uniformly. When defining a variable and specifying its type, use "character".

Following are all the keywords that you can use to convert the information into a structured format, Please ensure that you do not use any keywords other than these.

# bind
# Usage: Select any item that meets the conditions and assign it to the specified variable.
bind x: item where:
    is_light(x)

# achieve
# Usage: Specifies the state or relationship that needs to be achieved. Only states and relations can follow achieve, not types, properties, or other unchangeable content. You also cannot call functions or behaviors after achieve. If you need to call a function or a behavior, simply write the function directly without any keywords, just like calling a function in Python.
achieve is_on(light)

# foreach
# Usage: Iterates over all objects of a certain type. Note that you are not suppose to use "where" in foreach statement.
correct example:
foreach o: item:
    achieve closed(o)

error example:
foreach o: item where:
    achieve closed(o)
The where keyword was used in the error case.

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

# assert
# Usage: Asserts a condition that must be true for the behavior to succeed.
assert is_on(light)
    
# eff
# Usage: Represents the effect of an behavior. In this section, perform a series of bool assignments. Note that you should use [] instead of () here. Only the transition model will use this keyword. 
When you have additional information like this: A vacuum cleaner is a great tool for cleaning floors. You can carry it around to clean the floor. Before using it, please make sure the vacuum cleaner is plugged in and turned on.
You can define a transition model like this:
behavior clean_floow_with_vacuum(floor:item):
    goal: is_clean(floor)
    body:
        assert dirty(floor)
        bind vacuum: item where:
            is_vacuum_cleaner(vacuum)
        achieve inhand(vacuum)
        achieve is_plugged(vacuum)
        achieve is_on(vacuum)
        achieve walk(floor)
    eff:
        is_clean[floor]=True

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

- Wrong Version("place" in "body" of drop is not defined):
behavior drop(inhand_obj:item):
  goal: not inhand(inhand_obj)
  body:
    put(inhand_obj, place)

-> corrected version:
behavior drop(inhand_obj:item):
  goal: not inhand(inhand_obj)
  body:
    bind place: item where:
        surfaces(place) or recipient(place)
    put(inhand_obj, place)

In this example, the original version of the behavior definition contains an undefined variable place in the body of the behavior "drop". To correct this, I added the bind statement to define the variable place.   

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

## Output Format:
Output the goal representation with the supplemented definitions and declarations. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt

def other_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None):
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
- inhand(x: item)
Here are a few easily confusing usages to note:
In relationships with the _char suffix, the first parameter must always be a char. For example, on and on_char, inside and inside_char, close and close_char, facing and facing_char.

## available properties:
- surfaces(x: item)
- grabbable(x: item)
- sittable(x: item)
- lieable(x: item)
- hangable(x: item)
- drinkable(x: item)
- eatable(x: item)
- recipient(x: item)
- cuttable(x: item)
- pourable(x: item)
- can_open(x: item)
- has_switch(x: item)
- readable(x: item)
- lookable(x: item)
- containers(x: item)
- clothes(x: item)
- person(x: item)
- body_part(x: item)
- cover_object(x: item)
- has_plug(x: item)
- has_paper(x: item)
- movable(x: item)
- cream(x: item)
properties cannot be assigned a value; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions or assert statements.

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

# achieve
# Usage: Specifies the state or relationship that needs to be achieved. Only states and relations can follow achieve, not types, properties, or other unchangeable content. You also cannot call functions or behaviors after achieve. If you need to call a function or a behavior, simply write the function directly without any keywords, just like calling a function in Python.
achieve is_on(light)

# foreach
# Usage: Iterates over all objects of a certain type.
foreach o: item:
    achieve closed(o)

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

# assert
# Usage: Asserts a condition that must be true for the behavior to succeed.
assert is_on(light)
    
# eff
# Usage: Represents the effect of an behavior. In this section, perform a series of bool assignments. Note that you should use [] instead of () here. Only the transition model will use this keyword. 
When you have additional information like this: A vacuum cleaner is a great tool for cleaning floors. You can carry it around to clean the floor. Before using it, please make sure the vacuum cleaner is plugged in and turned on.
You can define a transition model like this:
behavior clean_floow_with_vacuum(floor:item):
    goal: is_clean(floor)
    body:
        assert dirty(floor)
        bind vacuum: item where:
            is_vacuum_cleaner(vacuum)
        achieve inhand(vacuum)
        achieve is_plugged(vacuum)
        achieve is_on(vacuum)
        achieve walk(floor)
    eff:
        is_clean[floor]=True

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

- Wrong Version("place" in "body" of drop is not defined):
behavior drop(inhand_obj:item):
  goal: not inhand(inhand_obj)
  body:
    put(inhand_obj, place)

-> corrected version:
behavior drop(inhand_obj:item):
  goal: not inhand(inhand_obj)
  body:
    bind place: item where:
        surfaces(place) or recipient(place)
    put(inhand_obj, place)

In this example, the original version of the behavior definition contains an undefined variable place in the body of the behavior "drop". To correct this, I added the bind statement to define the variable place.   

## Output Format:
Please refer to the error message and my provided syntax rules to correct the original goal representation. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt