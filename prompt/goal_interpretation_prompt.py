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
You need to analyze the goal and additional information that I provide(sometimes there may be no additional information), refer to the example, and transform them into the formal representation defined below. Your output may include several behaviors. In the body section of each behavior, you need to declare some intermediate states, intermediate relationships, final states, and final relationships required to achieve the goal. You do not need to provide the actions needed to achieve the goal. Once you provide the intermediate states, intermediate relationships, final states, and final relationships, my algorithm will plan a feasible sequence of actions on its own. Please note that the states, relationships, properties, and keywords you use must not exceed the scope I provided. If you call any function, make sure that you defined them already. Please check these problems carefully before outputting, otherwise the program will not run. Additionally, behavior __goal__(): is a required structure, functioning similarly to the main function in Python. You usually need to place it at the end of the output. Please do not provide any parameters to __goal__().
For additional information, sometimes you need to define a transition model. The characteristic of a transition model is that it includes an eff at the end of a behavior, indicating the effect of this behavior. Note that __goal__ behavior cannot be a transition model.

## The available states are (The text following the hash symbol is a comment; please do not include it in the goal representation):
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

# available behaviors (The text following the hash symbol is a comment; please do not include it in the goal representation):
The following behaviors can be directly invoked in the goal representation, with parameters passed in like function arguments.
- squeeze(obj:item) # To squeeze an item.
- move(obj:item) # To move an item.
- greet(person:item) # To greet a person.
- look_at(obj:item) # To look at an item.
- drink(obj: item) # To drink an item.
- watch(obj:item) # To watch an item.
- type(obj:item) # To type on an item.
- touch(obj:item) # To touch an item.
- read(obj:item) # To read an item.

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
    is_light(x)

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
achieve is_on(light)
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
assert is_on(light)

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

# exists
# Usage: Checks if there is at least one object that meets the condition and returns a boolean value.
template: exists obj_name: objtype : condition()
eg: exists item1: item : holds_lh(char, item1)

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

behavior __goal__():
    body:
        close_all_doors()

Example Analysis: 
This case aims to demonstrate the use of 'unordered' because to close a door, you must be close to it. When closing multiple doors, the order is very important. If you close the wrong door, it might block the path to another door. In such a case, you would have to reopen the already closed door to reach the other one, which might lead to the failure of the task. Therefore, the 'unordered' keyword is used here to automatically find the appropriate execution order.

# Example-4:
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

#Example-5:
A common mistake is ignoring the effective duration of "achieve." The effective duration of "achieve" persists until the current action is completed. In other words, after achieving inhand(A) within the same action, A will remain in hand, making it impossible to achieve other operations like on(A,B).

When the goal is: Put the apple on the table.
The additional information: None

A wrong output is:
behavior put_apple_on_table(apple:item,table:item):
    body:
        achieve inhand(apple)
        achieve on(apple,table)

Example Analysis:In this example, the apple must both remain in hand and be placed on the table, which is impossible to achieve. The solution to this problem is to remove the unnecessary step of achieving inhand(apple), as the program will automatically determine how to achieve on(apple,table).
A correct output is:
behavior put_apple_on_table(apple:item,table:item):
    body:
        achieve on(apple,table)

# Example-6:
when the goal is: Clean and dry a towel.
The additional information: Wash the towel in the sink and wring it out.

The output is:
behavior clean_towel(towel:item,sink:item):
    body:
        achieve inside(towel, sink)
        if exists faucet: item : is_faucet(faucet) and on(faucet,sink):
            achieve_once is_on(faucet)
            achieve_once is_off(faucet)
    eff:
        dirty[towel] = False
        clean[towel] = True

behavior dry_towel(towel:item):
    body:
        squeeze(towel)

behavior __goal__():
    body:
        bind towel: item where:
            is_towel(towel)
        bind sink: item where:
            is_sink(sink)
        clean_towel(towel,sink)
        dry_towel(towel)
    
Example Analysis: In this example, I want to demonstrate how to invoke available behaviors while highlighting the use of the exists keyword and the achieve_once keyword. Please pay particular attention to these aspects. First, according to the goal, we need to clean and dry a towel. So, the overall goal is divided into two steps: cleaning and drying. During the cleaning process, based on additional information, we need to use a sink to clean the towel. Therefore, in the __goal__, first, use bind to find the towel and sink. Please note that bind should only be used in __goal__ whenever possible. Next, design the clean_towel behavior, which uses two items: the towel and the sink, both of which were instantiated in the __goal__. According to common sense, the towel needs to be placed in the sink first. If the sink has a faucet, turn on the faucet to clean the towel, and then turn it off. Since the available states include clean and dirty, in the eff, the towel is set to clean. Secondly, for the wringing stage, directly invoke the available behavior and provide the necessary parameter towel. In principle, the dry_towel behavior should include an eff representing dryness. However, since the available states do not include a state representing dryness, this part is omitted.

## Output Format:
You can only output the description of the converted goal and additional information. Do not include any explanation or any other symbols.

"""
    return prompt