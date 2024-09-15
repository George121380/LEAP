def loop_refine(goal,cat_list=None,additional_information=None,action_sequence=None,goal_representation=None):
    if additional_information==None:
        additional_information="None"
    categories=""
    for cat in cat_list:
        categories+="- is_"+cat+"(x: item)\n"
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""
The goal representation is: """+goal_representation+"""
The sequence of actions is: """+action_sequence+"""
## Task Instructions:
To solve complex planning tasks, I have formalized the goal and additional information into the following goal representation based on the syntax rules defined below. By using a planner to parse the goal representation, I obtained the following sequence of actions. Please use common sense to check the sequence of actions and determine if there are any unreasonable actions. Based on this, please modify my goal representation accordingly.
t is important to note that when modifying the goal representation, you must adhere to the syntax rules I have defined and only use the given categories, states, relationships, and attributes. Otherwise, the program will consider it unexecutable.

## The available states are (The text following the hash symbol is a comment; please do not include it in the target representation):
- is_on(x: item) #is working
- is_off(x: item) #is not working
- plugged(x: item) 
- unplugged(x: item)
- open(x: item)
- closed(x: item)
- dirty(x: item)
- clean(x: item)
- sliced(food: item)
- peeled(food: item)
- mixed(container: item) #The word "mix" can only be used after a container, indicating the mixing of all items within the container.
- fried(food: item) # use pan to fry food
- boiled(food: item) # use pot to boil food
- grilled(food: item) # use oven to grill food
- waterfull(container: item)
- inhand(x: item)
Note that the mixed state can only be used for containers, not for food. 
wrong: mixed(milk)
correct: mixed(bowl)
And the fried state and boiled state can only be used for food, not for a container.
wrong: fried(pan)
correct: fried(egg)

## The available relationships are (The text following the hash symbol is a comment; please do not include it in the target representation):
- on(x: item, y: item)
- on_char(x: character, y: item)
- inside(x: item, y: item)
- inside_char(x: character, y: item)
- between(door: item, room: item)
- close(x: item, y: item)
- close_char(x: character, y: item)
Here are a few easily confusing usages to note:
In relationships with the _char suffix, the first parameter must always be a char. For example, on and on_char, inside and inside_char, close and close_char, facing and facing_char.

## available properties (The text following the hash symbol is a comment; please do not include it in the target representation):
- surfaces(x: item) # To indicate an item has a surface where things can be placed, such as a kitchen countertop or a table.
- grabbable(x: item) # To indicate an item can be grabbed in hand.
- cuttable(x: item) # To indicate an item can be cut with a knife.
- pourable(x: item) # To indicate an item can be poured into another container.
- can_open(x: item) 
- has_switch(x: item)
- containers(x: item) # To indicate an item is a container, such as a bowl, pot, or fridge.
- has_plug(x: item)
- peelable(x: item) # To indicate an item can be peeled, such as an apple or a potato.
- eatable(x: item) # To indicate an item can be eaten.
- cookaware(x: item) # To indicate an item can be used for cooking, such as a pan, oven, or a pot.
- storable(x: item) # To indicate an item can be used to temporarily store other objects, such as a countertop.
properties cannot be assigned a value; they can only return a boolean value as a predicate. For example, an apple can be grabbed, so grabbable(apple) will return true. Properties are typically used in if conditions or assert statements.

## available category determination:
"""+categories+"""
For any instance x:item, you can use is_y(x) to determine if x belongs to category y. You cannot perform any operations on a category; you can only determine the status and relationships of specific instances within a category. If you want to select an item instance that belongs to the category "box", you can use:
bind b: item where:
    is_box(b)
At the same time, if the category you want to use is not in the available category, please try to find its synonym or a similar category with a close function.
eg:
- food -> is_food_food(), Although the first type of translation is intuitive, when is_food is not in the available category, but is_food_food is, such a replacement should be made.

- soapy_water -> is_cleaning_solution(), soapy water is not an available category, but cleaning solution is. They are functionally similar, so such a replacement should be made.

## Syntax rules and keywords:
"char" is a constant instance that represents a character(youself). And character is a basic type, which can only be used when defining a instance. When passing parameters, use "char" uniformly. When defining a variable and specifying its type, use "character".

Following are all the keywords that you can use to convert the information into a structured format, Please ensure that you do not use any keywords other than these.

# bind
# Usage: Select any item that meets the conditions and assign it to the specified variable. 
bind x: item where:
    is_apple(x)
When extracting multiple items of the same category in a behavior, special attention must be paid to ensure that the items taken out later are not the same as those taken out earlier.
bind apple1: item where:
    is_apple(apple1)
bind apple2: item where:
    is_apple(apple2) and apple1!=apple2
bind apple3: item where:
    is_apple(apple3) and apple1!=apple3 and apple2!=apple3
To ensure consistency in the use of variables, try to use bind in __goal__ as much as possible and pass the retrieved instances as parameters to the invoked behaviors.

# achieve
# Usage: Specifies the state or relationship that needs to be achieved. Only states and relations can follow achieve, not types, properties, or other unchangeable content. You also cannot call functions or behaviors after achieve. If you need to call a function or a behavior, simply write the function directly without any keywords, just like calling a function in Python.
achieve is_on(countertop)
achieve not inhand(apple)

# achieve_once
# Usage: Specifies the state or relationship that needs to be achieved only once. This keyword is used when the state or relationship is temporary and does not need to be maintained to the end of the current behavior.
behavior wash(obj: item):
  goal: clean(obj)
  body:
    bind sink:item where:
      is_sink(sink)
    bind faucet:item where:
      is_faucet(faucet)
    achieve inside(obj, sink)
    achieve_once is_on(faucet)
    wash_executor(obj)
    achieve_once is_off(faucet)
  eff:
    dirty[obj] = False
    clean[obj] = True
    inside[obj, sink] = True

# foreach
# Usage: Iterates over all objects of a certain type. When using the "foreach" statement to operate on items, caution is needed. Many items exist in large quantities in the scene. Directly using "foreach" may lead to performing too many unnecessary operations. When only a few items need to be operated on, it might be better to use bind to extract the item to be operated on.
foreach o: item:
    if is_fridge(o) or is_cabinet(o):
        achieve closed(o)

# behavior
# Usage: Defines a behavior rule.
behavior turn_off_light(light:item):
    goal: is_off(light)
    body:
        achieve is_on(light)

# goal
# Usage: Specifies the goal condition for a behavior. If you want to use the goal, please ensure that you include all the parameters used in the goal in the behavior parameters.
behavior close_door(door:item):
    goal: closed(door)

# body
# Usage: Contains the sequence of actions and subgoals to achieve the behavior’s goal.
body:
    achieve close(a)
    achieve clean(b)

# assert
# Usage: Asserts a condition that must be true for the behavior to succeed.
assert is_on(stove)

#assert_hold
# Usage: The validity period of assert_hold lasts until the end of the containing behavior. This keyword is designed to express a long-term constraint condition.
assert_hold closed(fridge)
    
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

# available actions(The text following the hash symbol is a comment):
These are all the actions you can perform：
walk(x: item) # get close to the specified item
switchoff(x: item) # turn off the item x
switchon(x: item) # turn on the item x
put(x: item, y: item) # put the item x on the item y
grab(x: item) # grab the item x and let item x inhand
wash(x: item) # wash the item x and make it clean
open(x: item)  # open an item with property "can_open"
close(x: item) # close an item with property "can_open"
plugin(x: item) 
plugout(x: item)
stir(x: item) # stir and mix the item x, x should be a container
slice(x: item) # slice the item x, x should be a food
peel(x: item) # peel the item x, x should be a food

## Examples of correct goal represenations:
          
# Example-1:
When the goal is:
Clean all the plates and cups with dishwasher. Then put them on the table.

The additional information is:
- Dishwasher is a good way to clean plates and cups.
- The dishwasher must be closed and turned on to start the cleaning process.

The output is:
behavior clean_all_plates_and_cups_by_dishwasher(dishwasher:item):
    body:
        foreach o: item:
            if is_plate(o) or is_cup(o):
                achieve inside(o, dishwasher)
        achieve closed(dishwasher)
        achieve is_on(dishwasher)

behavior put_all_plates_and_cups_on_table(table:item):
    body:
        
        foreach o: item:
            if is_plate(o) or is_cup(o):
                achieve on(o, table)

behavior __goal__():
    body:
        bind dishwasher: item where:
            is_dishwasher(dishwasher)
        bind table: item where:
            is_table(table)
        clean_all_plates_and_cups(dishwasher)
        put_all_plates_and_cups_on_table(table)
    

Example Analysis: 
Completing this goal involves two stages: washing dishes and cups with a dishwasher, then put them on the table. First, all the dishes and cups need to be placed into the dishwasher, then the dishwasher must be closed and started. After washing, the dishes and cups need to be placed on the dining table.

# Example-2:
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

behavior __goal__():
    body:
        close_all_doors()

Example Analysis: 
This case aims to demonstrate the use of 'unordered' because to close a door, you must be close to it. When closing multiple doors, the order is very important. If you close the wrong door, it might block the path to another door. In such a case, you would have to reopen the already closed door to reach the other one, which might lead to the failure of the task. Therefore, the 'unordered' keyword is used here to automatically find the appropriate execution order.

# Example-3:
When the goal is: I want to eat an apple, clean an apple for me.
The additional information: Do not use the knife.

The output is:
behavior __goal__():
    body:
        bind apple: item where:
            is_apple(apple)
        for all o: item:
            if is_knife(o):
                assert_hold not inhand(knife)
        achieve clean(apple)

Example Analysis:
In this case, the challenge is to make sure that the knife is not used. The 'assert_hold' keyword is used to ensure that the knife is not in hand during the whole process. Notice that the 'assert_hold' keyword always gives a stronger restriction that the whole behavior must follow. So it is only used to express those constrains declared in additional information.

#Example-4:
When the goal is: Whisk an egg.
The additional information: None

The output is:
behavior whisk_an_egg(egg:item, bowl:item):
    body:
        achieve inside(egg, bowl)
        achieve peeled(egg)
        achieve mixed(bowl)

behavior __goal__():
    body:
        bind egg: item where:
            is_egg(egg)
        bind bowl: item where:
            is_bowl(bowl)
        whisk_an_egg(egg, bowl)

Example Analysis: The object to be mixed must be some kind of container, such as a pan, bowl, pot etc. So, to mix certain items, you must first ensure they are placed in a container, then bring the container to a mixed state.

#Example-5:
When the goal is: Help me make scrambled eggs with tomatoes
The additional information: To make sure it is healthy, wash the tomatoes and eggs before cooking. I don't like the skin of the tomatoes, so remove them before cooking.

The output is:
behavior prepare_tomato(tomato:item):
    body:
        achieve clean(tomato)        
        achieve peeled(tomato)
        achieve sliced(tomato)   

behavior prepare_egg(egg:item, bowl:item):
    body:
        achieve inside(egg, bowl)
        achieve mixed(bowl)

behavior cook_scrambled_eggs_with_tomatoes(pan:item, stove:item, tomato:item, egg:item, sugar:item, salt:item, oil:item):
    body:
        achieve on(pan, stove)
        achieve is_on(stove)
        achieve inside(tomato, pan)
        achieve inside(egg, pan)
        achieve inside(sugar, pan)
        achieve inside(salt, pan)
        achieve inside(oil, pan)
        achieve mixed(pan)

behavior __goal__():
    body:
        bind pan: item where:
            is_pan(pan)
        bind stove: item where:
            is_stove(stove)
        bind tomato: item where:
            is_tomato(tomato)
        bind egg: item where:
            is_egg(egg)
        bind bowl: item where:
            is_bowl(bowl)
        bind sugar: item where:
            is_sugar(sugar)
        bind salt: item where:
            is_salt(salt)
        bind oil: item where:
            is_oil(oil)
        prepare_tomato(tomato)
        prepare_egg(egg, bowl)
        cook_scrambled_eggs_with_tomatoes(pan, stove, tomato, egg, sugar, salt, oil)

Example Analysis:
When handling a complex goal, it can be broken down into several sub-goals. Here, making tomato scrambled eggs can be broken down into "prepare_tomato", "prepare_egg", and "cook_scrambled_eggs_with_tomatoes". In designing sub-goals, you need to design based on goals, additional information, and your common sense. Before invoking these sub-goal actions, ensure that all variables involved are defined and declared.
During the preparation of the tomatoes, according to additional information, they need to be washed and peeled. According to your common sense, skin removing should be done using the peeled state, and according to common sense, the tomatoes should be sliced before putting them into the pan, otherwise, they cannot be cooked.
For handling the eggs, since there is no additional information, it relies more on your common sense. The eggs should be cracked into a bowl and beaten until smooth before being put into the pan. Cracking the eggs into the bowl, due to the lack of a fully corresponding action, can be expressed as inside(egg, bowl), and beating them until smooth can be represented by the mixed state.
The cooking process also relies heavily on your common sense. First, you need to place the pan on the stove to preheat it, then add the prepared ingredients, followed by the various seasonings. Finally, stir everything evenly. Note that the stirring action is applied to the contents of the container as a whole, not to a specific ingredient.
In the goal_, you only need to invoke these sub-goals. Note that before invoking, you need to declare the corresponding variables, and when invoking, you need to pass the appropriate parameters.

#Example-6:
When the goal is: put a fried egg in the bowl
The additional information: None

A wrong output is:
behavior fry_egg(egg:item):
    body:
        achieve fried(egg)

behavior put_fried_egg_in_bowl():
    body:
        bind egg: item where:
            is_egg(egg)
        bind bowl: item where:
            is_bowl(bowl)
        achieve inside(egg, bowl)

behavior __goal__():
    body:
        cook_egg()
        put_fried_egg_in_bowl()

A correct output is:
behavior cook_egg(egg:item):
    body:
        achieve fried(egg)

behavior put_fried_egg_in_bowl(egg:item, bowl:item):
    body:
        achieve inside(egg, bowl)

behavior __goal__():
    body:
        bind egg: item where:
            is_egg(egg)
        bind bowl: item where:
            is_bowl(bowl)
        cook_egg(egg)
        put_fried_egg_in_bowl(egg, bowl)

Example Analysis:
Consistency between steps is a critical and error-prone issue. In wrong cases, the egg obtained using bind in put_fried_egg_in_bowl may not be the same egg that was previously fried in "fry_egg". Such a definition might result in egg_1 being fried but egg_2 being placed in the bowl. The correct case specifies the egg to be used in __goal__ and ensures that the same egg is operated on in both cook_egg and put_fried_egg_in_bowl through parameter passing.
Meanwhile, notice that fried() state and boiled state can only be used for food, rather than for a container.

#Behavior template:
The purpose of providing these templates is to prevent you from repeatedly proposing the same achieve objectives. You don't need to re-implement the following templates, just call the achieve goal in the templates.

When you execute achieve boiled(object), the following behavior will be executed.
behavior Boil(object:item):
  goal: boiled(object)
  body:
    bind stove:item where:
      is_stove(stove)
    bind pot:item where:
      is_pot(pot)
    achieve waterfull(pot)
    achieve on(pot, stove)
    achieve is_on(stove)
    achieve inside(object, pot)
  eff:
    boiled[object] = True

Behavior Explaination:
When you declare "achieve boiled(obj)" in the target expression, the program will automatically jump to this behavior. It will automatically find a stove and a pot, fill the pot with water, then place the pot on the stove, turn on the stove, and finally put the item to be boiled into the pot. Usually, you only need to declare "achieve boiled(obj)" and the program will automatically execute the above steps, without needing to repeat the involved steps. However, if you believe that the provided behavior cannot meet the current goal and additional information, you can design a new behavior by following the pattern of the provided behavior.But please note, if you design a new behavior, do not re-execute "achieve boiled," as this may lead to repeated actions.

When you execute achieve fried(object), the following behavior will be executed.
behavior Fry(object:item):
  goal: fried(object)
  body:
    bind pan:item where:
      is_pan(pan)
    bind stove:item where:
      is_stove(stove)
    achieve on(pan, stove)
    achieve is_on(stove)
    achieve inside(object, pan)
  eff:
    fried[object] = True

Behavior Explaination:
When you declare "achieve fried(obj)" in the target expression, the program will automatically jump to this behavior. It will automatically find a pan and a stove, place the pan on the stove, turn on the stove, and finally put the item to be fried into the pan. Usually, you only need to declare "achieve fried(obj)" and the program will automatically execute the above steps, without needing to repeat the involved steps. However, if you believe that the provided behavior cannot meet the current goal and additional information, you can design a new behavior by following the pattern of the provided behavior. But please note, if you design a new behavior, do not re-execute "achieve fried," as this may lead to repeated actions.

#Example-7:
A typical error case is when, after redefining how to prepare tomatoes and onions, "fried" is called again.This will cause the actions to be executed repeatedly.
behavior prepare_tomato_and_onion(tomato:item, onion:item):
    body:
        achieve sliced(tomato)
        achieve sliced(onion)
        bind pan:item where:
            is_pan(pan)
        bind stove:item where:
            is_stove(stove)
        achieve on(pan, stove)
        achieve is_on(stove)
        achieve inside(tomato, pan)
        achieve inside(onion, pan)
        achieve fried(tomato)
        achieve fried(onion)

Example Analysis:
In this case, what is given is a behavior definition rather than a complete goal representation. After specifying the preparation actions, calling "fried" again will result in many actions being executed repeatedly.

#Example-8:
As a general rule, a good habit is to remove the food after cooking.
when the goal is: Fry an egg.
The additional information: None

The output is:
behavior fry_egg(egg:item,container:item):
    body:
        achieve fried(egg)
        achieve inside(egg,container)

behavior __goal__():
    body:
        bind egg: item where:
            is_egg(egg)
        bind container: item where:
            is_plate(container) or is_bowl(container)
        fry_egg(egg,container)
        foreach dangerous_item: item:
            if is_stove(dangerous_item):
                achieve is_off(dangerous_item)
            if is_oven(dangerous_item):
                achieve is_off(dangerous_item)
            if is_faucet(dangerous_item):
                achieve is_off(dangerous_item)
        
Example Analysis:
This simple example demonstrates the importance of safety. After frying an egg, the stove, oven, and faucet should be turned off to avoid accidents. The use of "foreach" ensures that all dangerous items are turned off after the egg is fried. Meanwhile, food should be removed from the container after cooking, so the egg is placed inside the container after frying.

## Examples for modification:
My core objective is to have you modify and improve the original goal representation based on the feedback from the sequence of actions. Here are some examples of modifications for you to learn from and help me refine the goal representation I initially provided to you.

# Example-1:
The goal is: Make a humburger.
The additional information is: Clean all the ingredients before cooking. Do not use oven, which is broken. I want to make tomato paste and add it to the humburger.
The original goal representation is:
behavior clean_ingredients():
    body:
        foreach o: item:
            if is_tomato(o) or is_beef(o) or is_bread(o) or is_onion(o):
                achieve clean(o)

behavior make_tomato_paste(tomato:item, pan:item, stove:item):
    body:
        achieve sliced(tomato)
        achieve on(pan, stove)
        achieve is_on(stove)
        achieve inside(tomato, pan)
        achieve mixed(pan)

behavior cook_hamburger(beef:item, tomato_paste:item, bread:item, pan:item, stove:item, onion:item, cheese:item):
    body:
        achieve sliced(bread)
        achieve sliced(onion)
        achieve fried(beef)
        achieve on(pan, stove)
        achieve is_on(stove)
        achieve inside(beef, pan)
        achieve inside(tomato_paste, pan)
        achieve inside(bread, pan)
        achieve inside(onion, pan)
        achieve inside(cheese, pan)
        achieve mixed(pan)

behavior __goal__():
    body:
        bind tomato: item where:
            is_tomato(tomato)
        bind beef: item where:
            is_beef(beef)
        bind bread: item where:
            is_bread(bread)
        bind pan: item where:
            is_pan(pan)
        bind stove: item where:
            is_stove(stove)
        bind onion: item where:
            is_onion(onion)
        bind cheese: item where:
            is_cheese(cheese)
        clean_ingredients()
        make_tomato_paste(tomato, pan, stove)
        cook_hamburger(beef, pan, bread, pan, stove, onion, cheese)

Through the original goal representation, I obtained the following sequence of actions:
walk(fridge_18); open(fridge_18); walk(tomato_1); grab(tomato_1); walk(sink_20); put(tomato_1, sink_20); switchon(faucet_21); wash(tomato_1); switchoff(faucet_21); walk(tomato_2); grab(tomato_2); walk(sink_20); put(tomato_2, sink_20); switchon(faucet_21); wash(tomato_2); switchoff(faucet_21); walk(tomato_3); grab(tomato_3); walk(sink_20); put(tomato_3, sink_20); switchon(faucet_21); wash(tomato_3); switchoff(faucet_21); walk(tomato_4); grab(tomato_4); walk(sink_20); put(tomato_4, sink_20); switchon(faucet_21); wash(tomato_4); switchoff(faucet_21); walk(bread_26); grab(bread_26); walk(sink_20); put(bread_26, sink_20); switchon(faucet_21); wash(bread_26); switchoff(faucet_21); walk(onion_27); grab(onion_27); walk(sink_20); put(onion_27, sink_20); switchon(faucet_21); wash(onion_27); switchoff(faucet_21); walk(bread_30); grab(bread_30); walk(sink_20); put(bread_30, sink_20); switchon(faucet_21); wash(bread_30); switchoff(faucet_21); walk(bread_31); grab(bread_31); walk(sink_20); put(bread_31, sink_20); switchon(faucet_21); wash(bread_31); switchoff(faucet_21); walk(bread_32); grab(bread_32); walk(sink_20); put(bread_32, sink_20); switchon(faucet_21); wash(bread_32); switchoff(faucet_21); walk(beef_45); grab(beef_45); walk(sink_20); put(beef_45, sink_20); switchon(faucet_21); wash(beef_45); switchoff(faucet_21); walk(tomato_1); grab(tomato_1); walk(cuttingboard_44); put(tomato_1, cuttingboard_44); walk(knife_17); grab(knife_17); walk(tomato_1); slice(tomato_1); walk(pan_11); grab(pan_11); walk(stove_19); put(pan_11, stove_19); switchon(stove_19); walk(tomato_1); grab(tomato_1); walk(pan_11); put(tomato_1, pan_11); walk(spatula_22); grab(spatula_22); stir(pan_11); walk(countertop_23); put(knife_17, countertop_23); walk(bread_26); grab(bread_26); walk(cuttingboard_44); put(bread_26, cuttingboard_44); walk(knife_17); grab(knife_17); walk(bread_26); slice(bread_26); walk(countertop_23); put(knife_17, countertop_23); walk(onion_27); grab(onion_27); walk(cuttingboard_44); put(onion_27, cuttingboard_44); walk(knife_17); grab(knife_17); walk(onion_27); slice(onion_27); walk(countertop_23); put(knife_17, countertop_23); walk(beef_45); grab(beef_45); walk(pan_11); put(beef_45, pan_11); grab(pan_11); put(pan_11, pan_11); walk(bread_26); grab(bread_26); walk(pan_11); put(bread_26, pan_11); walk(onion_27); grab(onion_27); walk(pan_11); put(onion_27, pan_11); walk(cheese_29); grab(cheese_29); walk(pan_11); put(cheese_29, pan_11); stir(pan_11)

Issue Analysis:
In the clean_ingredients function, the foreach statement is used to clean all the tomatoes, beef, bread, and onions in the cleaning scene. First, although our goal is to "Clean all the ingredients," common sense tells us that beef and bread usually do not need to be washed, so the cleaning of beef and bread should be removed from the clean_ingredients function. Secondly, observing the generated sequence of actions, we see that all the tomatoes in the cleaning scene are cleaned, resulting in a total of four tomatoes being washed. However, common sense suggests that making a burger doesn't require so many tomatoes; usually, one tomato is enough. Therefore, the foreach statement should be modified to pass a single tomato obtained from the __goal__ through binding as a parameter to the clean_ingredients function, and only this one tomato should be washed.
The function make_tomato_paste is well-written and does not need any adjustments.
The cook_hamburger function should actually combine various ingredients into a hamburger. The assembly process itself should not take place in the pan but rather on a plate. Therefore, an additional bind statement should be added in the __goal__ to obtain a plate, and subsequent operations should be carried out on the plate. Additionally, a better way to make a hamburger is to stack the various ingredients, so using the on relationship would be more appropriate. Also, since there are two slices of bread, two slices should be obtained in the bind, and it should be noted that the second slice of bread should be different from the first.
To ensure that the oven is not used throughout the process, an assert_hold statement can be added to the __goal__.

Modified Goal Representation:
behavior clean_ingredients(tomato:item,onion:item):
    body:
        achieve clean(tomato)
        achieve clean(onion)

behavior make_tomato_paste(tomato:item, pan:item, stove:item):
    body:
        achieve sliced(tomato)
        achieve on(pan, stove)
        achieve is_on(stove)
        achieve inside(tomato, pan)
        achieve mixed(pan)

behavior cook_hamburger(beef:item, tomato_paste:item, bread_bottom:item, bread_top:item, onion:item, cheese:item, plate:item):
    body:
        achieve sliced(onion)
        achieve fried(beef)
        achieve on(bread_bottom, plate)
        achieve on(beef, bread_bottom)
        achieve on(tomato_paste, beef)
        achieve on(onion, tomato_paste)
        achieve on(cheese, onion)
        achieve on(bread_top, cheese)

behavior __goal__():
    body:
        bind tomato: item where:
            is_tomato(tomato)
        bind beef: item where:
            is_beef(beef)
        bind bread_bottom: item where:
            is_bread(bread_bottom)
        bind bread_top: item where:
            is_bread(bread_top)
        bind pan: item where:
            is_pan(pan)
        bind stove: item where:
            is_stove(stove)
        bind onion: item where:
            is_onion(onion)
        bind cheese: item where:
            is_cheese(cheese)
        bind plate: item where:
            is_plate(plate)
        foreach oven: item:
            if is_oven(oven):
                assert_hold closed(oven)
        clean_ingredients(tomato,onion)
        make_tomato_paste(tomato, pan, stove)
        cook_hamburger(beef, tomato, bread_bottom,bread_top, onion, cheese, plate)

# Example-2:
The goal is: Make Beef and Potato Stew.
The additional information is: Cut beef into bite-sized pieces. Season with salt and pepper. In a large pot, heat vegetable oil over medium-high heat. Brown the beef in batches, then remove and set aside. In the same pot, add more oil if needed. Sauté chopped onions and minced garlic until soft. Add tomato paste and cook for a minute. Add diced potatoes. Stir well. Return the beef to the pot. Bring to a boil. Season with additional salt and pepper to taste.

The original goal representation is:
behavior brown_beef(beef:item):
    body:
        bind oil: item where:
            is_oil(oil)
        bind stove: item where:
            is_stove(stove)
        bind pot: item where:
            is_pot(pot)
        achieve on(pot, stove)
        achieve is_on(stove)
        achieve inside(oil, pot)
        achieve fried(beef)

behavior cook_stew(beef:item, potato:item, onion:item, garlic:item, beef_broth:item):
    body:
        bind oil: item where:
            is_oil(oil)
        bind tomato_paste: item where:
            is_tomato(tomato_paste)
        bind stove: item where:
            is_stove(stove)
        bind pot: item where:
            is_pot(pot)
        assert_hold is_on(stove)
        achieve inside(oil, pot)
        achieve inside(onion, pot)
        achieve inside(garlic, pot)
        achieve inside(tomato_paste, pot)
        achieve is_on(stove)
        achieve inside(beef, pot)
        achieve inside(potato, pot)
        achieve inside(beef_broth, pot)
        achieve boiled(beef)
        achieve boiled(potato)

behavior prepare_ingredients(beef:item, potato:item, onion:item, garlic:item):
    body:
        achieve sliced(beef)
        achieve sliced(potato)
        achieve sliced(onion)
        achieve sliced(garlic)

behavior __goal__():
    body:
        bind beef: item where:
            is_beef(beef)
        bind potato: item where:
            is_potato(potato)
        bind onion: item where:
            is_onion(onion)
        bind garlic: item where:
            is_garlic(garlic)
        bind beef_broth: item where:
            is_beef(beef_broth)
        prepare_ingredients(beef, potato, onion, garlic)
        brown_beef(beef)
        cook_stew(beef, potato, onion, garlic, beef_broth)

Through the original goal representation, I obtained the following sequence of actions:
walk(fridge_18); open(fridge_18); walk(beef_45); grab(beef_45); walk(cuttingboard_44); put(beef_45, cuttingboard_44); walk(knife_17); grab(knife_17); walk(beef_45); slice(beef_45); walk(potato_46); grab(potato_46); walk(cuttingboard_44); put(potato_46, cuttingboard_44); walk(potato_46); slice(potato_46); walk(onion_27); grab(onion_27); walk(cuttingboard_44); put(onion_27, cuttingboard_44); walk(onion_27); slice(onion_27); walk(garlic_36); grab(garlic_36); walk(cuttingboard_44); put(garlic_36, cuttingboard_44); walk(garlic_36); slice(garlic_36); walk(pot_33); grab(pot_33); walk(stove_19); put(pot_33, stove_19); switchon(stove_19); walk(oil_9); grab(oil_9); walk(pot_33); put(oil_9, pot_33); walk(pan_11); grab(pan_11); walk(stove_19); put(pan_11, stove_19); walk(beef_45); grab(beef_45); walk(pan_11); put(beef_45, pan_11); walk(onion_27); grab(onion_27); walk(pot_33); put(onion_27, pot_33); walk(garlic_36); grab(garlic_36); walk(pot_33); put(garlic_36, pot_33); walk(tomato_1); grab(tomato_1); walk(pot_33); put(tomato_1, pot_33); walk(beef_45); grab(beef_45); walk(pot_33); put(beef_45, pot_33); walk(potato_46); grab(potato_46); walk(pot_33); put(potato_46, pot_33); grab(pot_33); walk(sink_20); put(pot_33, sink_20); switchon(faucet_21)

Issue Analysis:
First, to ensure the consistency of variable instances, all bind operations should be performed in the __goal__ behavior as much as possible. Secondly, some details were missing in the original goal representation. For example, the instruction "Season with salt and pepper" involves two items, salt and pepper, in the scene, so the statements achieve on(salt, beef) and achieve on(pepper, beef) were added in prepare_ingredients. Additionally, for "Add tomato paste and cook for a minute," the original implementation directly put the tomato into the pot. However, it is possible to design the process of making tomato paste, so the behavior make_tomato_paste was added. In brown_beef, the original representation used fried(beef), but according to the instructions, all cooking should be done in the pot. Since frying is done in a pan, fried was changed to boiled, which is performed in water. Moreover, according to the additional information, the beef should be placed in a bowl after browning rather than staying in the pot, so achieve inside(beef, bowl) was added. In cook_stew, the additional information specifies that salt and pepper should be added, so achieve inside(salt, pot) and achieve inside(pepper, pot) were added.

Modified Goal Representation:
behavior brown_beef(beef:item, pot:item, stove:item, bowl:item,oil:item):
    body:
        achieve on(pot, stove)
        achieve is_on(stove)
        achieve inside(oil, pot)
        achieve boiled(beef)
        achieve inside(beef, bowl)

behavior make_tomato_paste(tomato:item, bowl:item):
    body:
        achieve sliced(tomato)
        achieve inside(tomato, bowl)
        achieve mixed(bowl)

behavior cook_stew(beef:item, potato:item, onion:item, garlic:item,pot:item,stove:item,oil:item,tomato_paste:item, salt:item,pepper:item):
    body:
        achieve on(pot,stove)
        achieve is_on(stove)
        achieve inside(oil, pot)
        achieve inside(onion, pot)
        achieve inside(garlic, pot)
        achieve inside(tomato_paste, pot)
        achieve inside(potato, pot)
        achieve inside(beef, pot)
        achieve boiled(potato)
        achieve inside(salt, pot)
        achieve inside(pepper, pot)

behavior prepare_ingredients(beef:item, salt:item, pepper:item, potato:item, onion:item, garlic:item):
    body:
        achieve sliced(beef)
        achieve on(salt, beef)
        achieve on(pepper, beef)    
        achieve sliced(potato)
        achieve sliced(onion)
        achieve sliced(garlic)

behavior __goal__():
    body:
        bind beef: item where:
            is_beef(beef)
        bind salt: item where:
            is_salt(salt)
        bind pepper: item where:
            is_pepper(pepper)
        bind potato: item where:
            is_potato(potato)
        bind onion: item where:
            is_onion(onion)
        bind garlic: item where:
            is_garlic(garlic)
        bind pot: item where:
            is_pot(pot)
        bind bowl: item where:
            is_bowl(bowl)
        bind oil: item where:
            is_oil(oil)
        bind stove: item where:
            is_stove(stove)
        bind tomato: item where:
            is_tomato(tomato)
        prepare_ingredients(beef,salt,pepper, potato, onion, garlic)
        brown_beef(beef,pot,stove,bowl,oil)
        make_tomato_paste(tomato,bowl)
        cook_stew(beef, potato, onion, garlic,pot,stove,oil,tomato,salt,pepper)

# Example-3:
The goal is: I want to fry a chicken breast, and then heat some vegetables in the same pan.
The additional information is: take out the chicken breast before heating the vegetables.

The original goal representation is:
behavior cook_chicken_breast(chicken:item, pan:item, stove:item):
    body:
        achieve on(pan, stove)
        achieve is_on(stove)
        achieve inside(chicken, pan)
        achieve fried(chicken)
        achieve not inside(chicken, pan)

behavior heat_vegetables_in_pan(vegetables:item, pan:item, stove:item):
    body:
        achieve inside(vegetables, pan)
        achieve fried(vegetables)

behavior __goal__():
    body:
        bind chicken: item where:
            is_chicken(chicken)
        bind vegetables: item where:
            is_vegetables(vegetables)
        bind pan: item where:
            is_pan(pan)
        bind stove: item where:
            is_stove(stove)
        cook_chicken_breast(chicken, pan, stove)
        heat_vegetables_in_pan(vegetables, pan, stove)

Through the original goal representation, I obtained the following sequence of actions:
walk(pan_11); grab(pan_11); walk(stove_19); put(pan_11, stove_19); switchon(stove_19); walk(fridge_18); open(fridge_18); walk(chicken_35); grab(chicken_35); walk(pan_11); put(chicken_35, pan_11); walk(vegetables_38); grab(vegetables_38); walk(pan_11); put(vegetables_38, pan_11)

Issue Analysis:
Based on the action sequence for the chicken, it is clear that the additional information "take out the chicken breast before heating the vegetables" has not been met. In the original goal statement, there are two issues. First, the duration of "achieve" lasts until the end of the current behavior, so "achieve inside(chicken, pan)" and "achieve not inside(chicken, pan)" cannot be executed within the same behavior. If you want to use this approach, you need to change "achieve" to "achieve_once." However, a better way is to use common sense and designate a place to put the chicken, rather than using the original "achieve not inside(chicken, pan)" which is an uncontrollable program. In my modified version, you can choose a plate or bowl to temporarily store the chicken.

Modified Goal Representation:
behavior cook_chicken_breast(chicken:item):
    body:
        achieve fried(chicken)
        bind container: item where:
            is_plate(container) or is_bowl(container)
        achieve inside(chicken, container)

behavior heat_vegetables_in_pan(vegetables:item, pan:item):
    body:
        achieve fried(vegetables)

behavior __goal__():
    body:
        bind chicken: item where:
            is_chicken(chicken)
        bind vegetables: item where:
            is_vegetables(vegetables)
        bind pan: item where:
            is_pan(pan)
        cook_chicken_breast(chicken)
        heat_vegetables_in_pan(vegetables, pan)

## Output Format:
You can only output the description of the modified goal represenation. Do not include any explanation or any other symbols.
"""
    return prompt