def planning_not_found_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None):
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
I am converting my goals and additional information into a formal representation. Currently, my formal representation contains undefined category or predicate names. Please correct the errors in the formal representation based on the error messages.
Prioritize using synonyms to replace the undefined category names. If that's not possible, use categories with similar functions. However, under all circumstances, ensure that the corrected item categories appear in the available categories. I will demonstrate how to make replacements in the example section.

## Formal Representation with Error:
""" + goal_representation + """

## Error Log:
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

def planning_unknown_prompt(goal,cat_list=None,additional_information=None,goal_representation=None,error_info=None,behavior_from_library=None):
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
Important Note: The inhand(x) state is unique. If you intend to use inhand(x), you must implement it using the achieve_once keyword. At the same time, please note that you can take at most two items. Having too many items in hand will result in no solution.

## Available Relationships:
Please note: The text following each hash symbol (#) is a comment and should not be included in the current sub-task goal representation. 
- on(x: item, y: item) # item x is on top of item y
- on_char(x: character, y: item) # character is on item y (Character is you self. Any other animal like cat is an item)
- inside(x: item, y: item) # item x is inside item y, and y should be a room or a container
- inside_char(x: character, y: item) # character is inside item y (Character is you self. Any other animal like cat is an item)
- close(x: item, y: item) # item x is close to item y
- close_char(x: character, y: item) # character is close to item y (Character is you self. Any other animal like cat is an item)
Important Usage Notes: In relationships with the '_char' suffix, the first parameter must always be a char. For example, 'on' and 'on_char', 'inside' and 'inside_char', 'close' and 'close_char'.

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
- wipe(obj:item) # Wipe an item.
- squeeze(obj:item) # Squeeze an item.
- rinse(obj:item) # Rinse an item.
- move(obj:item) # Move an item.
- pull(obj:item) # Pull an item.
- push(obj:item) # Push an item.
- type(obj:item) # Type on an item.
- touch(obj:item) # Touch an item.
- read(obj:item) # Read an item.
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
"char" is a constant instance representing a character (yourself) and we assume that other animals like cat is an item. The type "character" can only be used when defining an instance. Use "char" consistently when passing parameters, and use "character" when defining a variable and specifying its type.

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
    achieve closed(a)
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
Please refer to the method used in the examples below to modify the goal representation I provided in this round, supplementing the missing definitions and declarations. Each example below will provide both wrong and correct versions, so you can learn how I make the modifications.

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
behavior view_neighborhood_from_bathroom_window():
    body:
        bind bathroom: item where:
            is_bathroom(bathroom)
        bind window: item where:
            is_window(window) and inside(window, bathroom)
        achieve close_char(self, bathroom)

-> corrected version:
behavior view_neighborhood_from_bathroom_window():
    body:
        bind bathroom: item where:
            is_bathroom(bathroom)
        bind window: item where:
            is_window(window) and inside(window, bathroom)
        achieve close_char(char, bathroom)

In this example, the original version of the behavior definition contains an undefined variable self in the body of the behavior "view_neighborhood_from_bathroom_window". Use "char" directly to represent itself.

Please note that, you can not provide any parameters to __goal__().
At the same time, please note that when you modify the parameters of a function or behavior, don't forget to also modify the function or behavior call statements to add any missing parameters.

## Output Format:
Output the goal representation with the supplemented definitions and declarations. You just need to output the modified entire goal representations without adding any symbols, comments, or explanations.
"""
    return prompt