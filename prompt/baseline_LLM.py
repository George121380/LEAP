
def predicate_expl():
    prompt="""States of an Item:
    is_on(x: item): The item x is turned on.
    is_off(x: item): The item x is turned off.
    plugged(x: item): The item x is plugged into a power source.
    unplugged(x: item): The item x is unplugged from a power source.
    open(x: item): The item x, such as a door or container, is open.
    closed(x: item): The item x, such as a door or container, is closed.
    dirty(x: item): The item x is dirty.
    clean(x: item): The item x is clean.
    sitting(x: character): The character x is sitting.
    lying(x: character): The character x is lying down.
    sleeping(x: character): The character x is sleeping.
    standing(x: character): The character x is standing.
    cut(x: item): The item x has been cut.
    inhand(x: item): The item x is currently in someone’s hand.

Relationships:
    on(x: item, y: item): The item x is on top of the item (y).
    inside(x: item, y: item): The item x is inside the item (y).
    between(door: item, room: item): The door x is between two rooms.
    close(x: item, y: item): The item x is near or close to the item (y).
    facing(x: item, y: item): The item x is facing towards the item (y).
    close_char(x: character, y: item): The character x is near or close to the item (y).
    facing_char(x: character, y: item): The character x is facing towards the item (y).
    inside_char(x: character, y: item): The character x is inside the item (y).
    on_char(x: character, y: item): The character x is on top of the item (y).
    on_body(x: item, y: character): The item x is attached to or worn by the character (y).
    holds_rh(x: character, y: item): The character x is holding the item (y) in their right hand.
    holds_lh(x: character, y: item): The character x is holding the item (y) in their left hand.

Properties:
    surfaces(x: item): The item x has a flat surface suitable for placing things.
    grabbable(x: item): The item x can be grabbed or picked up.
    sittable(x: item): The item x is suitable for sitting on.
    lieable(x: item): The item x is suitable for lying on.
    hangable(x: item): The item x can be hung or suspended.
    drinkable(x: item): The item x is suitable for drinking.
    eatable(x: item): The item x is suitable for eating.
    recipient(x: item): The item x is a recipient, suitable for holding things.
    cuttable(x: item): The item x can be cut.
    pourable(x: item): The item x can be poured (e.g., liquid).
    can_open(x: item): The item x can be opened.
    has_switch(x: item): The item x has a switch.
    readable(x: item): The item x can be read (e.g., a book).
    lookable(x: item): The item x can be looked at or observed.
    containers(x: item): The item x is a container.
    person(x: item): The item x is a person.
    body_part(x: item): The item x is a body part.
    cover_object(x: item): The item x can cover or protect other items.
    has_plug(x: item): The item x has a plug.
    has_paper(x: item): The item x contains paper.
    movable(x: item): The item x can be moved.
    cream(x: item): The item x is a type of cream.
    is_clothes(x: item): The item x is clothing.
    """

    return prompt

def primitive_actions():
    prompt="""Primitive Actions (The actions that you can execute):
walk_executor(x: item): get close to the item x.
switchoff_executor(x: item): turns off the item x.
switchon_executor(x: item): turns on the item x.
put_executor(x: item, y: item): places the item x onto the item y.( Both solid and liquid are acceptable.)
putin_executor(x: item, y: item): places the item x inside the item y. (Both solid and liquid are acceptable.)
grab_executor(x: item): grabs or picks up the item x. Note that you can only grab an item by one hand at a time. If you have grabbed an item with one hand you can not grab this item again before you put it down.
standup_executor(x: character): assists the character x in standing up from their current position.
wash_executor(x: item): washes or cleans the item x.
scrub_executor(x: item): scrubs the item x to clean it.
rinse_executor(x: item): rinses the item x with water.
sit_executor(x: item): sits down on the item x.
lie_executor(x: item): lies down on the item x.
open_executor(x: item): opens the item x, such as a door or container.
close_executor(x: item): closes the item x, such as a door or container.
plugin_executor(x: item): plugs in the item x.
plugout_executor(x: item): unplugs the item x.
cut_executor(x: item): cuts the item x.
wipe_executor(x: item): wipes or cleans the surface of the item x.
puton_executor(x: item): puts on the item x, such as clothing or an accessory.
putoff_executor(x: item): takes off or removes the item x.
touch_executor(x: item): touches or makes contact with the item x.
type_executor(x: item): types on or interacts with the item x, such as a keyboard.
push_executor(x: item): pushes the item x.
pull_executor(x: item): pulls the item x.
"""
    # print(prompt)
    return prompt

def guidance():
    prompt="""Guidance:
    - For unknown items, move to the location where they are most likely to be. If you believe the item is inside a container, such as a refrigerator, open the container to check. Once you successfully approach the item, you will receive an observation that can be used to update your knowledge.
    - Limit yourself to holding a maximum of two items at any given time.
    - Before retrieving an item from a closed container, ensure the container is opened first.
    - To fill a container with water, hold a container (e.g., a cup), approach the faucet, turn it on, and then turn it off. Ignore the precise details, such as the exact duration the faucet should remain open.
    - If both of your hands are occupied and you need to free one, place the item on a surface.
    - To turn off an appliance, switch it off before interacting with it. When switching on an appliance, ensure it is closed first.
    - When cutting something, place it on a cutting board and hold the knife to cut.
    - You can only interact with an object when you walk close to it.
    - You must an appliance is turned off before open it. (e.g., fridge, oven)
    - You must make sure an appliance is plugged in before turning it on.
    """
    return prompt

def LLM_Agent_Prompt(goal:str, add_info:str, item_info:str,action_history:str,unknown_items:list,char_information:str,human_exp_guidance:str):
    predicate=predicate_expl()
    pr_act=primitive_actions()
    guid=guidance()
    unknown_items_info=""
    if len(unknown_items)>0:
        unknown_items_info="\n#Unknown Items\n"
        unknown_items_info+="""The following items have not been found yet. If you want to use or operate them, you need to search for them in known locations first.:\n"""
        for item in unknown_items:
            unknown_items_info+=f"{item}\n"
        add_info+='\n'
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

    prompt+="""
#Task Instruction
Your task is to output the next action that should be performed to complete the specified task based on the provided information. The output should contain only the action, with no explanations.

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

#Output Format
Your output must contain only one of the primitive actions, using the correct parameters as defined. For example, if you want to walk to the area near sink_42, use walk_executor(sink_42). If you want to open fridge_289, output open_executor(fridge_289). Ensure that your output contains no explanations, as this may cause the output to be unrecognized.
"""
    
    with open('prompt.txt','w') as f:
        f.write(prompt)

    return prompt
