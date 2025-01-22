
def predicate_expl():
    prompt="""States of an Item:
    is_on: The item is turned on.
    is_off: The item is turned off.
    plugged: The item is plugged into a power source.
    unplugged: The item is unplugged from a power source.
    open: The item, such as a door or container, is open.
    closed: The item, such as a door or container, is closed.
    dirty: The item is dirty.
    clean(x: item): The item is clean.
    has_water(x: item) : The item has water inside or on it.
    cut(x: item): The item has been cut.
    inhand(x: item): The item is currently in someone’s hand.

Properties:
    surfaces: The item has a flat surface suitable for placing things.
    grabbable: The item can be grabbed or picked up.
    sittable: The item is suitable for sitting on.
    lieable: The item is suitable for lying on.
    hangable: The item can be hung or suspended.
    drinkable: The item is suitable for drinking.
    eatable: The item is suitable for eating.
    recipient: The item is a recipient, suitable for holding things.
    cuttable: The item can be cut.
    pourable: The item can be poured (e.g., liquid).
    can_open: The item can be opened.
    has_switch: The item has a switch.
    readable: The item can be read (e.g., a book).
    lookable: The item can be looked at or observed.
    containers: The item is a container.
    person: The item is a person.
    body_part: The item is a body part.
    cover_object: The item can cover or protect other items.
    has_plug: The item has a plug.
    has_paper: The item contains paper.
    movable: The item can be moved.
    cream: The item is a type of cream.
    is_clothes: The item is clothing.
    is_food: Indicates that the item is food.
    """

    return prompt

def primitive_actions():
    prompt="""Primitive Actions (The actions that you can execute):
walk_executor(x: item): get close to the item. (Preconditions: The character must be standing, and the item must not be unknown.)
switchoff_executor(x: item): turns off the item. (Preconditions: The item must have a switch, the character must have a free hand, and the character must be close to the item.)
switchon_executor(x: item): turns on the item. (Preconditions: The item must have a switch, the character must have a free hand, the item must not be unknown, and if the item has a plug, it must be plugged in; if it can be opened, it must be closed, and the character must be close to the item.)
put_executor(x: item, y: item): places the item onto the item y.(Preconditions: The items x and y must not be unknown, the character must have the item in hand, and the character must be close to the item y.)
putin_executor(x: item, y: item): places the item inside the item y. (Preconditions: The item y must be a recipient, container, openable, or eatable; the items x and y must not be unknown; if y is openable, it must be opened; the character must have the item in hand and be close to the item y.)
grab_executor(x: item): grabs or picks up the item. (Preconditions: The item must be grabbable or water, the item must not be unknown, the character must have a free hand, if x is inside another item and that item is openable, it must be opened, and the character must be close to the item.)
standup_executor(x: character): assists the character x in standing up from their current position.
wash_executor(x: item): washes or cleans the item. (Preconditions: The item must not be unknown, the character must have a free hand, and the character must be close to the item.)
scrub_executor(x: item): scrubs the item to clean it. (Preconditions: The item must not be unknown, the character must have a free hand, and the character must be close to the item.)
rinse_executor(x: item): rinses the item with water. (Preconditions: The item must not be unknown, the character must have a free hand, and the character must be close to the item.)
sit_executor(x: item): sits down on the item. (Preconditions: The item must be sittable, the item must not be unknown, and the character must be close to the item.)
lie_executor(x: item): lies down on the item. (Preconditions: The item must be lieable, the item must not be unknown, and the character must be close to the item.)
open_executor(x: item): opens the item, such as a door or container. (Preconditions: The item must be openable, the item must not be unknown, the character must have a free hand, if the item has a switch and is on, it must be off, and the character must be close to the item.)
close_executor(x: item): closes the item, such as a door or container. (Preconditions: The item must be openable, the item must not be unknown, the character must have a free hand, and the character must be close to the item.)
plugin_executor(x: item): plugs in the item. (Preconditions: The item must have a plug, the item must not be unknown, the character must have a free hand, and the character must be close to the item.)
plugout_executor(x: item): unplugs the item. (Preconditions: The item must have a plug, the item must not be unknown, the character must have a free hand, if the item has a switch, it must be off, and the character must be close to the item.)
cut_executor(x: item): cuts the item. (Preconditions: The item must be cuttable or eatable, the item must not be unknown, the character must have a knife in hand, if there is a cutting board, the item must be on it, and the character must be close to the item.)
wipe_executor(x: item): wipes or cleans the surface of the item. (Preconditions: The item must not be unknown, the character must have a cleaning tool in hand (e.g., towel, sponge), and the character must be close to the item.)
touch_executor(x: item): touches or makes contact with the item. (Preconditions: The item must not be unknown, if x is inside another item, that item must be openable, a recipient, or eatable; if it is openable, it must be opened, and the character must be close to the item.)
type_executor(x: item): types on or interacts with the item, such as a keyboard. (Preconditions: The item must be a keyboard or have a switch, the item must not be unknown, and the character must be close to the item.)
push_executor(x: item): pushes the item. (Preconditions: The item must be movable, a button, a chair, or a curtain, the item must not be unknown, the character must have a free hand, and the character must be close to the item.)
pull_executor(x: item): pulls the item. (Preconditions: The item must be movable, a button, a chair, or a curtain, the item must not be unknown, the character must have a free hand, and the character must be close to the item.)
"""
    # print(prompt)
    return prompt

def guidance():
    prompt="""Guidance:
    - For unknown items, move to the location where they are most likely to be. If you believe the item is inside a container, such as a refrigerator, open the container to check. Once you successfully approach the item, you will receive an observation that can be used to update your knowledge.
    - Limit yourself to holding a maximum of two items at any given time.
    - Before retrieving an item from a closed container, ensure the container is opened first.
    - To fill a container with water, hold a container (e.g., a cup), approach the faucet, turn it on, and then turn it off. Ignore the precise details, such as the exact duration the faucet should remain open. Assume that all actions are performed correctly and imidiately.
    - If both of your hands are occupied and you need to free one, place the item on a surface.
    - To turn off an appliance, switch it off before interacting with it. When switching on an appliance, ensure it is closed first.
    - When cutting something, place it on a cutting board and hold the knife to cut.
    - You can only interact with an object after you walk close to it.
    - You must make sure an appliance is turned off before open it. (e.g., fridge, oven)
    - You must make sure an appliance is plugged in before turning it on.
    """
    return prompt

def LLM_Agent_Prompt(goal:str, add_info:str, item_info:str,action_history:str,unknown_items:list,char_information:str,human_exp_guidance:str):
    predicate=predicate_expl()
    pr_act=primitive_actions()
    guid=guidance()
    unknown_items_info=""

    # -----------------------------------------------------
    # List all the unknown items directly?
    # if len(unknown_items)>0:
    #     unknown_items_info="\n#Unknown Items\n"
    #     unknown_items_info+="""The following items have not been found yet. If you want to use or operate them, you need to search for them around known locations first:\n"""
    #     for item in unknown_items:
    #         unknown_items_info+=f"{item}\n"
    #     add_info+='\n'


    prompt=''
    if len(action_history)==0:
        action_history_info="No actions have been performed yet."
    else:
        action_history_info="These are some actions you have taken to complete the current task.\n"
        for id in range(len(action_history)):
            if 'action' in action_history[id] and 'effects' in action_history[id]:
                action_history_info+=f"Action {id+1}: {(action_history[id]['action'])} -> effect: {action_history[id]['effects']}\n"
            else:
                action_history_info+=f"Trial and error when action {id+1}: {action_history[id]}"

    human_exp_guidance_info=""
    if len(human_exp_guidance)>0:
        human_exp_guidance_info="\n#Human Expert Guidance\n"
        human_exp_guidance_info+="The following is some guidance provided by a human expert:\n"
        human_exp_guidance_info+=human_exp_guidance

    if len(add_info)>0:
        add_info="\n#Additional Information\n"+add_info
        


    prompt+="""
#Task Instruction
Your task is to output a sequence of actions that should be performed to complete the specified task based on the provided information. The output should contain only a actions list, with no explanations.

#Goal
"""+goal+"""
"""+unknown_items_info+"""
"""+human_exp_guidance_info+"""
"""+add_info+"""
#Character Information
"""+char_information+"""

#Primitive Actions
"""+pr_act+"""

#Action History
"""+action_history_info+"""

#Predicates
"""+predicate+"""

#Guidance
"""+guid+"""

#Item Information
The following is some information about items related to the task.
"""+item_info+"""

#Examples
['walk_executor(kitchen_counter_1234)', 'walk_executor(fridge_567)', 'switchoff_executor(fridge_567)', 'open_executor(fridge_567)', 'wash_executor(food_vegetable_890)', 'walk_executor(pot_432)', 'open_executor(pot_432)', 'walk_executor(food_vegetable_890)', 'grab_executor(food_vegetable_890)', 'walk_executor(pot_432)', 'putin_executor(food_vegetable_890, pot_432)', 'grab_executor(pot_432)', 'walk_executor(stove_789)', 'put_executor(pot_432, stove_789)', 'switchon_executor(stove_789)', 'walk_executor(cupboard_345)', 'open_executor(cupboard_345)', 'walk_executor(wallshelf_678)', 'walk_executor(wallshelf_901)', 'walk_executor(wallshelf_234)', 'walk_executor(sink_567)', 'walk_executor(table_890)', 'walk_executor(food_vegetable_890)', 'grab_executor(food_vegetable_890)', 'walk_executor(bowl_123)', 'putin_executor(food_vegetable_890, bowl_123)']

#Output Format
Your output must be a Python list, where each element is a string representing a single primitive action. Ensure that your output contains no explanations or additional text, as this may cause the output to be unrecognized.
"""
    
    with open('visualization/prompt.txt','w') as f:
        f.write(prompt)

    return prompt
