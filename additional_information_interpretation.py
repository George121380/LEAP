from openai import OpenAI

def ask_GPT(system,content):
    with open("/Users/liupeiqi/workshop/Research/api_key.txt","r") as f:
        api_key = f.read().strip()
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content":content}
        ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def get_goal_inter_prompt(goal,item_list=None):
    items=""
    for item in item_list:
        items+="- "+item+"\n"
    prompt="""
The goal is: """+goal+""".
## Task Instructions:
Analyze the provided goal and convert it into a description similar to the Example. Your output should include: defining some goal functions, designing some behaviors. In the body section of behavior, write out the required states or relationships. Finally, output a standalone goal that only includes the goal function. 
Your goal can be divided into three parts: target state, target relationship, and target action. The first two are more commonly used, while the target action is only declared with the keyword "do" when you believe a specific action must be executed.
Unless you are very sure that a specific action must be executed, do not use the keyword "do." Your main task is to provide the intermediate states, intermediate relationships, final state, and final relationships needed to achieve the goal. Once you provide these states and relationships, the algorithm will recursively plan actions and automatically search for a series of actions.

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

## The available executable actions are:
- walk_executor(x: item)
- switchoff_executor(x: item)
- switchon_executor(x: item)
- put_executor(x: item, y: item)
- grab_executor(x: item)
- standup_executor(x: character)
- wash_executor(x: item)
- sit_executor(x: character)
- open_executor(x: item)
- close_executor(x: item)
- pour_executor(x: item, y: item)
- plugin_executor(x: item)
- plugout_executor(x: item)

## We have these items in the scene:
"""+items+"""

## Here are the keywords that you can use:
Following are all the keywords that you can use to convert the goal into a structured format, Please ensure that you do not use any keywords other than these.
# do
# Usage: Executes a primitive controller function.
do open_executor(x)

# bind
# Usage: Declares a variable and assigns it a value, often with constraints.
bind x: Pose = find_position(o)

# foreach
# Usage: Iterates over all objects of a certain type.
foreach o: item:
    achieve closed(o)

# exist
# Usage: Checks if a variable with a certain property exists.
exist p: item : is_on(p)

# behavior
# Usage: Defines a behavior rule.
behavior move_away(o: Object, t: Trajectory)
goal: not blocking(o, t)
body:
    do move(o, t)

# goal
# Usage: Specifies the goal condition for a behavior.
goal: clean(o)

# body
# Usage: Contains the sequence of actions and subgoals to achieve the behavior’s goal.
body:
  achieve close(a)
  achieve clean(b)

# promotable
# Usage: Allows unordered and interleaved execution of subgoals.
body:
  promotable:
    achieve close(a)
    achieve clean(b)

# if-else
# Usage: Conditional statement for branching logic.
if condition:
    achieve close(a)
else:
    achieve clean(b)


## Example-simple:
When the goal is: 
I find the groceries and carry them into the kitchen. I place them on the counter and begin to sort them out. I place the vegetables, eggs, cheese, and milk in the fridge.

The output is:
behavior __goal__():
  body:
    promotable:
      achieve inside(vegetables_8, fridge_68)
      achieve inside(eggs_19, fridge_68)
      achieve inside(cheese_908, fridge_68)
      achieve inside(milk_171, fridge_68)

# Example-hard:
When the goal is:
Clean all the plates and cups with dishwasher. Then put them on the table.

The output is:

behavior clean_all_plates_and_cups():
  body:
    promotable:
      achieve inside(plate_1004, dishwasher_81)
      achieve inside(plate_1005, dishwasher_81)
      achieve inside(cup_1001, dishwasher_81)
      achieve inside(cup_1003, dishwasher_81)
    achieve closed(dishwasher_81)
    achieve is_on(dishwasher_81)

behavior put_all_plates_and_cups_on_table():
  body:
    promotable:
      achieve on(plate_1004, table_63)
      achieve on(plate_1005, table_63)
      achieve on(cup_1001, table_63)
      achieve on(cup_1003, table_63)

behavior __goal__():
  body:
    clean_all_plates_and_cups()
    put_all_plates_and_cups_on_table()
    

Example Analysis: In this case, clean_all_plates_and_cups declares a series of intermediate states, and put_all_plates_and_cups_on_table declares a series of final states. The promotable keyword can only be used once within a body. Therefore, when the task is complex, multiple behaviors can be defined and then called in the __goal__ to represent complex tasks that require multiple promotable definitions. It should be noted that in clean_all_plates_and_cups, the order of putting plates and cups into the dishwasher is arbitrary, so these inside states are marked with the promotable keyword. However, the dishwasher can only be closed and started after all the plates and cups to be cleaned are inside, so promotable cannot include closed and is_on. The processes of inside, closed, and is_on must be executed in order.

## Output Format:
You can only output the description of the converted goal. Do not include any explanation or any other symbols.
"""
    return prompt

def interpretation(goal,item_list=None):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system = "I have a goal described in natural language, and I need it converted into a structured format."
    content = get_goal_inter_prompt(goal,item_list)

    print('=' * 80)
    print(f"When Goal instruction is: {goal}")
    converted_content=ask_GPT(system,content)
    print('=' * 80)
    print("The Goal interpretation is:\n")
    print('=' * 80)

    return converted_content



if __name__ == '__main__':
    
    goal="put the apple on the light"
    item_list=["dining_room","broom","floor","dustpan","dirt","trashcan","apple","light"]
    interpretation(goal,item_list)
    
    
